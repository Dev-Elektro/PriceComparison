# -*- coding: utf-8 -*-
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from bs4 import BeautifulSoup
from searchengine.engine import ProductItem
from searchengine.webdriver import Driver
from selenium.common.exceptions import TimeoutException
from loguru import logger as log


class citilink:
    def __init__(self, driver: Driver):
        self.browser = driver.getBrowser()

    def _parseProductCard(self, url: str):
        """Разбор страницы товара с характеристиками"""
        try:
            self.browser.get(f"{url}properties/")
            # Ожидание загрузки всех ajax-запросов
            WebDriverWait(self.browser, timeout=5).until(ec.visibility_of_element_located((By.CLASS_NAME, 'SpecificationsFull')))
            contentHtml = self.browser.find_element(By.ID, 'content').get_attribute('innerHTML')
            contentHtml = BeautifulSoup(contentHtml, 'lxml')
            productName = contentHtml.find('h1', {'class': 'ProductHeader__title'}).get_text(strip=True)
            productPrice = contentHtml.find('span', {'class': 'ProductHeader__price-default_current-price'}).get_text(strip=True).replace(' ', '')
            specificationsHtml = contentHtml.find('div', {'class': 'TabContent'}).find_all('div', {'class': 'Specifications__row'})
            specifications = []
            for item in specificationsHtml:
                try:
                    name = item.find('div', {'class': 'Specifications__column_name'}).get_text(strip=True)
                    value = item.find('div', {'class': 'Specifications__column_value'}).get_text(strip=True)
                    specifications.append({'name': name, 'value': value})
                except Exception:
                    continue
            yield ProductItem(productName, productPrice, url, specifications)
        except TimeoutException as e:
            log.warning(e)
            return None

    def search(self, query):
        """Функция поиска по сайту"""
        try:
            self.browser.get(f"https://www.citilink.ru/search/?text={query}")
            currentUrl = self.browser.current_url
            if 'search' in currentUrl:
                try:
                    WebDriverWait(self.browser, timeout=5).until(
                        ec.visibility_of_element_located((By.CLASS_NAME, 'ProductCardCategoryList__grid')))
                except Exception:
                    return None

                grid = self.browser.find_element(By.CLASS_NAME, 'ProductCardCategoryList__grid')
                soup = BeautifulSoup(grid.get_attribute('innerHTML'), 'lxml')
                elements = soup.find_all('div', {'class': 'ProductCardVertical'})
                for element in elements:
                    try:
                        productName = element.find('a', {'class': 'ProductCardVertical__name'}).get('title')
                        productPrice = element.find('span', {
                            'class': 'ProductCardVerticalPrice__price-current_current-price'}).get_text(
                            strip=True).replace(" ", "")
                        link = f"https://www.citilink.ru{element.find('a', {'class': 'ProductCardVertical__name'}).get('href')}"
                    except Exception:
                        continue
                    yield ProductItem(productName, productPrice, f'{link}', None)
            elif 'product' in currentUrl:
                return self._parseProductCard(currentUrl)
        except TimeoutException as e:
            log.warning(e)
            return None
