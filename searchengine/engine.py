from typing import Protocol, NamedTuple, Iterable
from multiprocessing.pool import ThreadPool
from searchengine.utils import findPartNumber, wordProcessing
from searchengine.webdriver import Driver
import re
from loguru import logger as log


class ProductItem(NamedTuple):
    """Объект товара. Содержин наименование, цену, адрес в каталоге магазина, характеристики"""
    name: str
    price: str
    url: str
    specifications: list


class ResultItem(NamedTuple):
    """Объект результата поска. Содержит наименование запроса, номер стороки в таблице и спикок найденых товаров"""
    queryValue: str  # Текст запроса
    rowNum: int  # Номер строки в таблице
    listProduct: list[ProductItem]  # Список найденых товаров


class SearchPoolItem(NamedTuple):
    """Объект процесса поиска. Содержит наименование сайта, наименование таблицы и столбца для записи резутатов и список результатов"""
    name: str  # Наименование сайта
    sheetName: str
    columnName: str  # Наименование колонки для записи результата
    result: list[ResultItem]  # Результат процесса поиска


class QueryItem(NamedTuple):
    """Объект запроса для поиска. Содержит номер строки в таблице и текста запроса."""
    rowNum: int  # Номер строки
    value: str  # Текст запроса


class WebSite(Protocol):
    """Интерфейс для послучения дынных со страницы поиска на сайтах"""
    def search(self, query: str) -> Iterable[ProductItem]:
        raise NotImplementedError


class SearchPool:
    def __init__(self, processes=1, headless=True):
        self._pool = ThreadPool(processes=processes)
        self._processes = []
        self.headless = headless

    def __iter__(self):
        self._pos = 0
        return self

    def __next__(self):
        if self._pos < len(self._processes):
            res = SearchPoolItem(
                self._processes[self._pos][0],
                self._processes[self._pos][1],
                self._processes[self._pos][2],
                self._processes[self._pos][3].get()
            )
            self._pos += 1
            return res
        else:
            raise StopIteration

    def _search(self, site: WebSite, cells: Iterable) -> list[ResultItem]:
        """Поиск по списку с запросами из файла. Принимает функцию поиска и список запросов."""
        driver = Driver(headless=self.headless)  # Инициализация вебдрайвера
        driver.start()
        buf = []  # Буфер для найденых результатов, что бы дублирующиеся запросы не искать повторно.
        result = []
        for cell in cells:  # Перебераем ячейки
            log.debug(f"Запрос: {cell.value=}")
            fromBuf = list(filter(lambda x: x[0] == cell.value, buf))  # Проверяем результат для запроса в буфере
            if not fromBuf:
                log.debug("Запрос с сайта")
                res = [i for i in runSearchBySite(cell.value, site(driver))]  # Вызывов функции поиска с передачей вебдрайвера и текста поискового запроса. Результат собираем в список.
                buf.append([cell.value, res])
            else:
                log.debug("Найден в буфере")
                res = fromBuf[0][1]
            result.append(ResultItem(queryValue=cell.value, rowNum=cell.rowNum, listProduct=res))  # Формируем словарь с номером строки ячейки, текстом запроса и результатом поиска.
        driver.stop()
        return result

    def addTask(self, name: str, site: WebSite, listQuery: list, sheetName: str, columnName: str):
        self._processes.append((
            name,
            sheetName,
            columnName,
            self._pool.apply_async(self._search, [site, listQuery])
        ))


def _searchByPartNumber(partNumber: str, site: WebSite) -> Iterable[ProductItem]:
    """Поиск по партномеру"""
    for item in site.search(partNumber):  # Получаем поисковый ответ от сайта
        buf = item.name
        if spec := item.specifications:  # Если в результате поика есть спецификации, то их собираем в строку
            buf += f"{' '.join(map(lambda x: str(x.get('value')), spec))}"
        if partNumber in buf:  # Проверка совподает ли парт номер с результатом поска
            yield item


def _searchByText(query: str, site: WebSite) -> Iterable[ProductItem]:
    """Поиск по тексту"""
    for query_proc in wordProcessing(query):
        emptyData = True
        interationStop = False
        for item in site.search(query_proc):
            emptyData = False
            regex = r"[\w-]{3,}"
            buf = item.name
            if spec := item.specifications:
                buf += f"{' '.join(map(lambda x: str(x.get('value')), spec))}"
            query_word = re.findall(regex, query.lower(), re.MULTILINE | re.UNICODE)
            result_word = re.findall(regex, buf.lower(), re.MULTILINE | re.UNICODE)
            overlap = sum(True for word in query_word if word in result_word)
            if overlap == len(query_word):
                interationStop = True
                yield item
        if emptyData or interationStop:
            return


def runSearchBySite(query: str, site: WebSite) -> Iterable[ProductItem]:
    """Поск по интерисующему сайту, возвращает список ProductItem"""
    if partNumber := findPartNumber(query):
        return _searchByPartNumber(partNumber, site)
    return _searchByText(query, site)
