# -*- coding: utf-8 -*-
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from bs4 import BeautifulSoup
from searchengine.engine import ProductItem
from searchengine.webdriver import Driver
from selenium.common.exceptions import TimeoutException
from loguru import logger as log


class dnsshop:
    """Парсер для сайта dns-shop.ru"""
    def __init__(self, driver: Driver) -> None:
        self.browser = driver.getBrowser()

    def _parseProductCard(self, url: str):
        """Разбор страницы товара с характеристиками"""
        try:
            self.browser.get(f"{url}characteristics/")
            WebDriverWait(self.browser, timeout=5).until(ec.visibility_of_element_located((By.CLASS_NAME, 'product-card-description')))
            WebDriverWait(self.browser, timeout=5).until(ec.visibility_of_element_located((By.CLASS_NAME, 'product-buy__price')))
            contentHtml = self.browser.find_element(By.CSS_SELECTOR, '.container.product-card').get_attribute('innerHTML')
            contentHtml = BeautifulSoup(contentHtml, 'lxml')
            if contentHtml.find('div', {'class': 'order-avail-wrap order-avail-wrap_not-avail'}):
                return None
            productName = contentHtml.find('h1', {'class': 'product-card-top__title'}).get_text(strip=True).replace('Характеристики ', '')
            productPrice = contentHtml.find('div', {'class': 'product-buy__price'}).get_text(strip=True).replace(' ', '')[:-1]
            specificationsHtml = contentHtml.find('div', {'class': 'product-card-description'}).find_all('div', {'class': 'product-characteristics__spec'})
            specifications = []
            for item in specificationsHtml:
                try:
                    name = item.find('div', {'class': 'product-characteristics__spec-title'}).get_text(strip=True)
                    value = item.find('div', {'class': 'product-characteristics__spec-value'}).get_text(strip=True)
                    specifications.append({'name': name, 'value': value})
                except Exception:
                    continue
            yield ProductItem(productName, productPrice, url, specifications)
        except TimeoutException as e:
            log.warning(e)
            return None

    def search(self, query: str):
        """Поиск по сайту и парсинг результата"""
        try:
            self.browser.get(f"https://www.dns-shop.ru/search/?q={query}")
            currentUrl = self.browser.current_url
            if 'search' in currentUrl or 'catalog' in currentUrl:
                try:
                    WebDriverWait(self.browser, timeout=5).until(
                        ec.visibility_of_element_located((By.CLASS_NAME, 'products-list__content')))
                    WebDriverWait(self.browser, timeout=5).until(
                        ec.visibility_of_element_located((By.CLASS_NAME, 'product-buy__price-wrap')))
                    WebDriverWait(self.browser, timeout=5).until(
                        ec.visibility_of_element_located((By.CLASS_NAME, 'order-avail-wrap')))
                except Exception:
                    return None

                grid = self.browser.find_element(By.CLASS_NAME, 'products-list')
                soup = BeautifulSoup(grid.get_attribute('innerHTML'), 'lxml')
                elements = soup.find_all('div', {'class': 'catalog-product'})
                for element in elements:
                    try:
                        productName = element.find('a', {'class': 'catalog-product__name'}).get_text(strip=True)
                        productPrice = element.find('div', {'class': 'product-buy__price'}).get_text(
                            strip=True).replace(" ", "")[:-1]
                        availability = False if 'Товара нет в наличии' in element.find('div', {
                            'class': 'order-avail-wrap'}).get_text(strip=True) else True
                        link = f"https://www.dns-shop.ru{element.find('a', {'class': 'catalog-product__name'}).get('href')}"
                    except Exception:
                        continue
                    if not availability:
                        continue
                    yield ProductItem(productName, productPrice, f'{link}', None)

            elif 'product' in currentUrl:
                return self._parseProductCard(currentUrl)
        except TimeoutException as e:
            log.warning(e)
            return None
