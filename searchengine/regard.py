# -*- coding: utf-8 -*-
from typing import Iterable
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from bs4 import BeautifulSoup
from searchengine.engine import ProductItem
from searchengine.webdriver import Driver
from selenium.common.exceptions import TimeoutException
from loguru import logger as log


class regard:
    def __init__(self, driver: Driver):
        self.name = "Regard"
        self.browser = driver.getBrowser()

    def _parseProductCard(self, url: str):
        """Разбор страницы товара с характеристиками"""
        try:
            self.browser.get(url)
            WebDriverWait(self.browser, timeout=5).until(ec.visibility_of_element_located((By.TAG_NAME, 'main')))
            content_html = self.browser.find_element(By.TAG_NAME, 'main').get_attribute('innerHTML')
            content_html = BeautifulSoup(content_html, 'lxml')
            product_name = content_html.find('h1', {'class': 'productPage_title__1B1Yw'}).get_text(strip=True)
            product_price = content_html.find('span', {'class': 'PriceBlock_price__3hwFe'}).get_text(strip=True).replace('\xa0', '')[:-1]
            specifications_html = content_html.find('div', {'class': 'Grid_row__ZvFHa productPage_bottom__2rdYu'}).find_all('li', {'class': 'CharacteristicsItem_li__hJ4YF'})
            specifications = []
            for item in specifications_html:
                try:
                    name = item.find('div', {'class': 'CharacteristicsItem_name__-AhRC'}).find('span').get_text(strip=True)
                    value = item.find('p', {'class': 'CharacteristicsItem_value__3-EWJ'}).find('span').get_text(strip=True)
                    specifications.append({'name': name, 'value': value})
                except Exception:
                    continue
            yield ProductItem(product_name, product_price, url, specifications)
        except TimeoutException as e:
            log.warning(e)
            return None

    @staticmethod
    def _parseProductList(elements: list) -> Iterable[ProductItem]:
        for element in elements:
            try:
                product_name = element.find('a', {'class': 'CardText_link__2H3AZ'}).get_text(strip=True)
                product_price = element.find('span', {'class': 'CardPrice_price__1t0QB'}).get_text(
                    strip=True).replace("\xa0", "")[:-1]
                link = f"https://www.regard.ru{element.find('a', {'class': 'CardText_link__2H3AZ'}).get('href')}"
            except Exception:
                continue
            yield ProductItem(product_name, product_price, f'{link}', None)

    def search(self, query: str):
        """Функция поиска по сайту"""
        try:
            self.browser.get(f"https://www.regard.ru/catalog?search={query}")
            current_url = self.browser.current_url
            if 'search' in current_url or 'catalog' in current_url:
                try:
                    WebDriverWait(self.browser, timeout=5).until(
                        ec.visibility_of_element_located((By.CLASS_NAME, 'rendererWrapper')))
                except Exception:
                    return None
                grid = self.browser.find_element(By.CLASS_NAME, 'rendererWrapper')
                soup = BeautifulSoup(grid.get_attribute('innerHTML'), 'lxml')
                elements = soup.find_all('div', {'class': 'Card_wrap__2fsLE'})
                log.debug("Parse product list")
                return self._parseProductList(elements)

            elif 'product' in current_url:
                log.debug("Parse product card")
                return self._parseProductCard(current_url)
        except TimeoutException as e:
            log.warning(e)
            return None
