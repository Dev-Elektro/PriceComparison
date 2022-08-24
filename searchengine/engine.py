from typing import Protocol, NamedTuple, Iterable, Callable
from multiprocessing.pool import ThreadPool
from multiprocessing import Lock
from searchengine.utils import findPartNumber, wordProcessing
from searchengine.webdriver import Driver
import re
from loguru import logger as log


class ProductItem(NamedTuple):
    """Объект товара. Содержит наименование, цену, адрес в каталоге магазина, характеристики"""
    name: str
    price: str
    url: str
    specifications: list


class ResultItem(NamedTuple):
    """Объект результата поиска. Содержит наименование запроса, номер строки в таблице и список найденных товаров"""
    queryValue: str  # Текст запроса
    rowNum: int  # Номер строки в таблице
    listProduct: list[ProductItem]  # Список найденных товаров


class SearchPoolItem(NamedTuple):
    """Объект процесса поиска. Содержит наименование сайта, наименование таблицы и
    столбца для записи результатов и список результатов"""
    name: str  # Наименование сайта
    sheetName: str
    columnName: str  # Наименование колонки для записи результата
    result: list[ResultItem]  # Результат процесса поиска


class QueryItem(NamedTuple):
    """Объект запроса для поиска. Содержит номер строки в таблице и текста запроса."""
    rowNum: int  # Номер строки
    value: str  # Текст запроса


class WebSite(Protocol):
    """Интерфейс для получения дынных со страницы поиска на сайтах"""
    def search(self, query: str) -> Iterable[ProductItem]:
        raise NotImplementedError


_file_to_write: Callable = None


def writeToFile(func: Callable) -> Callable:
    """Декоратор для указания файла для записи"""
    global _file_to_write
    _file_to_write = func
    return func


class SearchPool:
    global _file_to_write

    def __init__(self, processes=1, headless=True):
        self._cbWriteFile = _file_to_write
        self._pool = ThreadPool(processes=processes)
        self._processes = []
        self._headless = headless
        self._callback = None
        self._lock = Lock()

    def __iter__(self):
        self._pos = 0
        return self

    def __next__(self):
        if self._pos < len(self._processes):
            res = None
            try:
                res = SearchPoolItem(
                    self._processes[self._pos][0],
                    self._processes[self._pos][1],
                    self._processes[self._pos][2],
                    self._processes[self._pos][3].get()
                )
            except Exception as e:
                log.exception(e)
            self._pos += 1
            return res
        else:
            raise StopIteration

    def _search(self, name: str, sheet_name: str, column_name: str, site: WebSite, cells: Iterable) -> list[ResultItem]:
        """Поиск по списку с запросами из файла. Принимает функцию поиска и список запросов."""
        driver = Driver(headless=self._headless)  # Инициализация веб драйвера
        driver.start()
        buf = []  # Буфер для найденных результатов, что бы дублирующиеся запросы не искать повторно.
        result = []
        for pos, cell in enumerate(cells):  # Перебираем ячейки
            log.debug(f"Запрос: {cell.value}")
            from_buf = list(filter(lambda x: x[0] == cell.value, buf))  # Проверяем результат для запроса в буфере
            if not from_buf:
                log.debug("Запрос с сайта")
                # Поиск с передачей веб драйвера и текста поискового запроса. Результат собираем в список.
                res = [i for i in runSearchBySite(cell.value, site(driver))]
                buf.append([cell.value, res])
            else:
                log.debug("Найден в буфере")
                res = from_buf[0][1]
            if not isinstance(self._callback, type(None)):
                self._callback(name, len(cells), pos + 1)
            # Формируем словарь с номером строки ячейки, текстом запроса и результатом поиска.
            res_item = ResultItem(queryValue=cell.value, rowNum=cell.rowNum, listProduct=res)
            result.append(res_item)
            if not isinstance(self._cbWriteFile, type(None)):
                log.debug(f"{name} - готов к записи.")
                self._lock.acquire()
                log.debug(f"{name} - Пишем в файл.")
                self._cbWriteFile(name, sheet_name, column_name, res_item)
                self._lock.release()
        driver.stop()
        return result

    def addTask(self, name: str, site: WebSite, list_query: list, sheet_name: str, column_name: str):
        """Добавить задание. addTask(self, name: str, site: WebSite, listQuery: list, sheetName: str,
        columnName: str)"""
        self._processes.append((
            name,
            sheet_name,
            column_name,
            self._pool.apply_async(self._search, [name, sheet_name, column_name, site, list_query])
        ))

    def setCallback(self, func: Callable[[str, int, int], None]):
        """Обратный вызов для отображения хода процесса. Callback(siteName: str, totalCount: int, currentPos: int)"""
        self._callback = func

    def setWriteFile(self, func: Callable[[str, str, str, ResultItem], None]):
        """Обратный вызов для обработки найденного товара с ожиданием выполнения, передает (Имя сайта, Имя листа,
        Имя колонки, объект ResultItem"""
        self._cbWriteFile = func

    def wait(self):
        """Ожидание завершения работы потоков."""
        for p in self._processes:
            p[3].get()


def _searchByPartNumber(part_number: str, site: WebSite) -> Iterable[ProductItem]:
    """Поиск по парт номеру"""
    for item in site.search(part_number):  # Получаем поисковый ответ от сайта
        buf = item.name
        if spec := item.specifications:  # Если в результате поиска есть спецификации, то их собираем в строку
            buf += f"{' '.join(map(lambda x: str(x.get('value')), spec))}"
        if part_number in buf:  # Проверка совпадает ли парт номер с результатом поиска
            yield item


def _searchByText(query: str, site: WebSite) -> Iterable[ProductItem]:
    """Поиск по тексту"""
    for query_proc in wordProcessing(query):
        empty_data = True
        interation_stop = False
        for item in site.search(query_proc):
            empty_data = False
            regex = r"[\w-]{3,}"
            buf = item.name
            if spec := item.specifications:
                buf += f"{' '.join(map(lambda x: str(x.get('value')), spec))}"
            query_word = re.findall(regex, query.lower(), re.MULTILINE | re.UNICODE)
            result_word = re.findall(regex, buf.lower(), re.MULTILINE | re.UNICODE)
            overlap = sum(True for word in query_word if word in result_word)
            if overlap == len(query_word):
                interation_stop = True
                yield item
        if empty_data or interation_stop:
            return


def runSearchBySite(query: str, site: WebSite) -> Iterable[ProductItem]:
    """Поиск по интересующему сайту, возвращает список ProductItem"""
    if partNumber := findPartNumber(query):
        return _searchByPartNumber(partNumber, site)
    return _searchByText(query, site)
