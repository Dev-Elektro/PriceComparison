from typing import Callable, Union, Iterable

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Query

import json
from searchengine.types import ProductItem, WebSite


engine = create_engine('sqlite:///:memory:?cache=shared', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class Buffer(Base):
    """Модель таблицы в базе дынных для хранения результатов поисковых запросов.
    Содержит имя сайта, поисковый запрос и результат поиска."""
    __tablename__ = "buffer"

    id = Column(Integer, primary_key=True)
    site = Column(String)
    query = Column(String)
    result = Column(String)

    def __init__(self, site, query, result):
        super(Buffer, self).__init__()
        self.site = site
        self.query = query
        self.result = result


Base.metadata.create_all(engine)  # Создание таблиц в базе данных.


def addToBuffer(site_name: str, search_query: str, search_result_item: ProductItem) -> None:
    """Добавляет результат поискового запроса в буфер.
    Принимает имя сайта, текст запроса и результат поиска."""
    with Session() as session:
        buffer = Buffer(site_name, search_query, json.dumps(search_result_item))
        session.add(buffer)
        session.commit()


def _existInBuffer(site_name: str, search_query: str) -> Union[bool, Query]:
    """Проверка наличия сохраненных поисковых результатов в базе данных.
    Принимает имя сайта и текст поискового запроса."""
    with Session() as session:
        return session.query(Buffer).filter(Buffer.site == site_name, Buffer.query == search_query).first()


def _getFromBuffer(site_name: str, search_query: str) -> Iterable[ProductItem]:
    """Получить с буфера сохраненные результаты поиска.
    Принимает имя сайта и текст поискового запроса."""
    with Session() as session:
        for item in session.query(Buffer).filter(Buffer.site == site_name, Buffer.query == search_query).all():
            yield ProductItem(*json.loads(item.result))


def searchBuffer(func: Callable) -> Callable:
    """Декоратор для функции поиска, проверяет предварительно поисковый запрос в буфере."""
    def wrapper(query: str, site: WebSite):
        if _existInBuffer(site.name, query):
            return _getFromBuffer(site.name, query)
        return func(query, site)

    return wrapper
