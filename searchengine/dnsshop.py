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


class dnsshop(WebSite):
    """Парсер для сайта dns-shop.ru"""
    name = "DNS"

    def __init__(self, driver: Driver) -> None:
        self.name = "DNS-Shop"
        self.browser = driver.getBrowser()

    def _parseProductCard(self, url: str):
        """Разбор страницы товара с характеристиками"""
        log.debug(f"URL: {url}")
        try:
            self.browser.get(f"{url}characteristics/")
            WebDriverWait(self.browser, timeout=5).until(ec.visibility_of_element_located((By.CLASS_NAME, 'product-card-description')))
            WebDriverWait(self.browser, timeout=5).until(ec.visibility_of_element_located((By.CLASS_NAME, 'product-buy__price')))
            content_html = self.browser.find_element(By.CSS_SELECTOR, '.container.product-card').get_attribute('innerHTML')
            content_html = BeautifulSoup(content_html, 'lxml')
            if content_html.find('div', {'class': 'order-avail-wrap order-avail-wrap_not-avail'}):
                return []
            product_name = content_html.find('h1', {'class': 'product-card-top__title'}).get_text(strip=True).replace('Характеристики ', '')
            product_price = content_html.find('div', {'class': 'product-buy__price'}).get_text(strip=True)
            product_price = product_price.replace(' ', '').split('₽')[0]
            specifications_html = content_html.find('div', {'class': 'product-card-description'}).find_all('div', {'class': 'product-characteristics__spec'})
            specifications = []
            log.debug(product_name)
            for item in specifications_html:
                try:
                    name = item.find('div', {'class': 'product-characteristics__spec-title'}).get_text(strip=True)
                    value = item.find('div', {'class': 'product-characteristics__spec-value'}).get_text(strip=True)
                    specifications.append({'name': name, 'value': value})
                except Exception as e:
                    log.debug(e)
                    continue
            yield ProductItem(product_name, product_price, url, specifications)
        except TimeoutException as e:
            log.warning(e)
            return []

    @staticmethod
    def _parseProductList(elements: list) -> Iterable[ProductItem]:
        for element in elements:
            try:
                product_name = element.find('a', {'class': 'catalog-product__name'}).get_text(strip=True)
                product_price = element.find('div', {'class': 'product-buy__price'}).get_text(
                    strip=True).replace(" ", "")[:-1]
                availability = False if 'Товара нет в наличии' in element.find('div', {
                    'class': 'order-avail-wrap'}).get_text(strip=True) else True
                link = f"https://www.dns-shop.ru{element.find('a', {'class': 'catalog-product__name'}).get('href')}"
            except Exception:
                continue
            if not availability:
                continue
            yield ProductItem(product_name, product_price, f'{link}', None)

    def search(self, query: str) -> Iterable[ProductItem]:
        """Поиск по сайту и парсинг результата"""
        try:
            self.browser.get(f"https://www.dns-shop.ru/search/?q={query}")
            current_url = self.browser.current_url
            if 'search' in current_url or 'catalog' in current_url:
                try:
                    WebDriverWait(self.browser, timeout=5).until(
                        ec.visibility_of_element_located((By.CLASS_NAME, 'products-list__content')))
                    WebDriverWait(self.browser, timeout=5).until(
                        ec.visibility_of_element_located((By.CLASS_NAME, 'product-buy__price-wrap')))
                    WebDriverWait(self.browser, timeout=5).until(
                        ec.visibility_of_element_located((By.CLASS_NAME, 'order-avail-wrap')))
                except Exception:
                    return []

                grid = self.browser.find_element(By.CLASS_NAME, 'products-list')
                soup = BeautifulSoup(grid.get_attribute('innerHTML'), 'lxml')
                elements = soup.find_all('div', {'class': 'catalog-product'})
                log.debug("Parse product list")
                return self._parseProductList(elements)

            elif 'product' in current_url:
                log.debug("Parse product card")
                return self._parseProductCard(current_url)
        except TimeoutException as e:
            log.warning(e)
            return []

        return []
