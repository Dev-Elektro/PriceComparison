# -*- coding: utf-8 -*-
from typing import Iterable
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from bs4 import BeautifulSoup

from searchengine import WebSite
from searchengine.engine import ProductItem
from searchengine.webdriver import Driver
from selenium.common.exceptions import TimeoutException
from loguru import logger as log


class citilink(WebSite):
    def __init__(self, driver: Driver):
        self.name = "Citilink"
        self.browser = driver.getBrowser()

    def _parseProductCard(self, url: str):
        """Разбор страницы товара с характеристиками"""
        try:
            self.browser.get(f"{url}properties/")
            # Ожидание загрузки всех ajax-запросов
            WebDriverWait(self.browser, timeout=5).until(ec.visibility_of_element_located(
                (By.CLASS_NAME, 'SpecificationsFull')))
            content_html = self.browser.find_element(By.ID, 'content').get_attribute('innerHTML')
            content_html = BeautifulSoup(content_html, 'lxml')
            if "Нет в наличии" in str(content_html):
                return []
            product_name = content_html.select_one('div.Container > div > div > div h1').get_text(strip=True)
            product_price = content_html.select_one(
                'div.Container > div > div > div:nth-child(5) > section:nth-child(3) span > span'
                ).get_text(strip=True).replace(' ', '')
            specifications_html = content_html.find('div', {'class': 'TabContent'}) \
                .find_all('div', {'class': 'Specifications__row'})
            specifications = []
            for item in specifications_html:
                try:
                    name = item.find('div', {'class': 'Specifications__column_name'}).get_text(strip=True)
                    value = item.find('div', {'class': 'Specifications__column_value'}).get_text(strip=True)
                    specifications.append({'name': name, 'value': value})
                except Exception:
                    continue
            yield ProductItem(product_name, product_price, url, specifications)
        except TimeoutException as e:
            log.warning(e)
            return []

    @staticmethod
    def _parseProductList(elements: list) -> Iterable[ProductItem]:
        for element in elements:
            try:
                product_name = element.find('a', {'class': 'ProductCardVertical__name'}).get('title')
                product_price = element.find('span', {
                    'class': 'ProductCardVerticalPrice__price-current_current-price'}).get_text(
                    strip=True).replace(" ", "")
                link = f"https://www.citilink.ru{element.find('a', {'class': 'ProductCardVertical__name'}).get('href')}"
            except Exception:
                continue
            yield ProductItem(product_name, product_price, f'{link}', None)

    def search(self, query):
        """Функция поиска по сайту"""
        try:
            self.browser.get(f"https://www.citilink.ru/search/?text={query}")
            current_url = self.browser.current_url
            if 'search' in current_url:
                try:
                    WebDriverWait(self.browser, timeout=5).until(
                        ec.visibility_of_element_located((By.CLASS_NAME, 'ProductCardCategoryList__grid')))
                except Exception as e:
                    print(e)
                    log.debug(f"Oshibka poisk SITILINK {e}")
                    return []

                grid = self.browser.find_element(By.CLASS_NAME, 'ProductCardCategoryList__grid')
                soup = BeautifulSoup(grid.get_attribute('innerHTML'), 'lxml')
                elements = soup.find_all('div', {'class': 'ProductCardVertical'})
                log.debug("Parse product list")

                return self._parseProductList(elements)

            elif 'product' in current_url:
                log.debug("Parse product card")
                return self._parseProductCard(current_url)
        except TimeoutException as e:
            log.warning(e)
            return []
        return []
