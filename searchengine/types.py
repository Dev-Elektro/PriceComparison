from abc import abstractmethod
from typing import NamedTuple, Protocol, Iterable


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
    name: str

    @abstractmethod
    def search(self, query: str) -> Iterable[ProductItem]:
        raise NotImplementedError
