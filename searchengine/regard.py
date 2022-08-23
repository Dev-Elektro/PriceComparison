# -*- coding: utf-8 -*-
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
        self.browser = driver.getBrowser()

    def _parseProductCard(self, url: str):
        """Разбор страницы товара с характеристиками"""
        try:
            self.browser.get(url)
            WebDriverWait(self.browser, timeout=5).until(ec.visibility_of_element_located((By.TAG_NAME, 'main')))
            contentHtml = self.browser.find_element(By.TAG_NAME, 'main').get_attribute('innerHTML')
            contentHtml = BeautifulSoup(contentHtml, 'lxml')
            productName = contentHtml.find('h1', {'class': 'productPage_title__1B1Yw'}).get_text(strip=True)
            productPrice = contentHtml.find('span', {'class': 'PriceBlock_price__3hwFe'}).get_text(strip=True).replace('\xa0', '')[:-1]
            specificationsHtml = contentHtml.find('div', {'class': 'Grid_row__ZvFHa productPage_bottom__2rdYu'}).find_all('li', {'class': 'CharacteristicsItem_li__hJ4YF'})
            specifications = []
            for item in specificationsHtml:
                try:
                    name = item.find('div', {'class': 'CharacteristicsItem_name__-AhRC'}).find('span').get_text(strip=True)
                    value = item.find('p', {'class': 'CharacteristicsItem_value__3-EWJ'}).find('span').get_text(strip=True)
                    specifications.append({'name': name, 'value': value})
                except Exception:
                    continue
            yield ProductItem(productName, productPrice, url, specifications)
        except TimeoutException as e:
            log.warning(e)
            return None

    def search(self, query: str):
        """Функция поиска по сайту"""
        try:
            self.browser.get(f"https://www.regard.ru/catalog?search={query}")
            currentUrl = self.browser.current_url
            if 'search' in currentUrl or 'catalog' in currentUrl:
                try:
                    WebDriverWait(self.browser, timeout=5).until(
                        ec.visibility_of_element_located((By.CLASS_NAME, 'rendererWrapper')))
                except Exception:
                    return None
                grid = self.browser.find_element(By.CLASS_NAME, 'rendererWrapper')
                soup = BeautifulSoup(grid.get_attribute('innerHTML'), 'lxml')
                elements = soup.find_all('div', {'class': 'Card_wrap__2fsLE'})
                for element in elements:
                    try:
                        productName = element.find('a', {'class': 'CardText_link__2H3AZ'}).get_text(strip=True)
                        productPrice = element.find('span', {'class': 'CardPrice_price__1t0QB'}).get_text(
                            strip=True).replace("\xa0", "")[:-1]
                        link = f"https://www.regard.ru{element.find('a', {'class': 'CardText_link__2H3AZ'}).get('href')}"
                    except Exception:
                        continue
                    yield ProductItem(productName, productPrice, f'{link}', None)
            elif 'product' in currentUrl:
                return self._parseProductCard(currentUrl)
        except TimeoutException as e:
            log.warning(e)
            return None
