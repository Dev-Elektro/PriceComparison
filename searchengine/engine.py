from typing import Iterable, Callable
from multiprocessing.pool import ThreadPool
from multiprocessing import Lock

from searchengine.types import SearchPoolItem, WebSite, ResultItem, ProductItem
from searchengine.utils import findPartNumber, wordProcessing
from searchengine.webdriver import Driver
from searchengine.searchbuffer import addToBuffer, searchBuffer
import re
from loguru import logger as log


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
        result = []
        for pos, cell in enumerate(cells):  # Перебираем ячейки
            # Поиск с передачей веб драйвера и текста поискового запроса. Результат собираем в список.
            res = [i for i in runSearchBySite(cell.value, site(driver))]
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


@searchBuffer
def _searchByPartNumber(part_number: str, site: WebSite) -> Iterable[ProductItem]:
    """Поиск по парт номеру"""
    for item in site.search(part_number):  # Получаем поисковый ответ от сайта
        buf = item.name
        if spec := item.specifications:  # Если в результате поиска есть спецификации, то их собираем в строку
            buf += f"{' '.join(map(lambda x: str(x.get('value')), spec))}"
        if part_number in buf:  # Проверка совпадает ли парт номер с результатом поиска
            addToBuffer(site.name, part_number, item)
            yield item


@searchBuffer
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
                addToBuffer(site.name, query, item)
                yield item
        if empty_data or interation_stop:
            return


def runSearchBySite(query: str, site: WebSite) -> Iterable[ProductItem]:
    """Поиск по интересующему сайту, возвращает список ProductItem"""
    if partNumber := findPartNumber(query):
        return _searchByPartNumber(partNumber, site)
    return _searchByText(query, site)
