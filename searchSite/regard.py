# -*- coding: utf-8 -*-
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from bs4 import BeautifulSoup
from . import searchProcessing

def parseProductCard(browser, url):
    """Разбор страницы товара с характеристиками"""

    try:
        browser.get(url)
        WebDriverWait(browser, timeout=5).until(ec.visibility_of_element_located((By.TAG_NAME, 'main')))
        contentHtml = browser.find_element(By.TAG_NAME, 'main').get_attribute('innerHTML')
        contentHtml = BeautifulSoup(contentHtml, 'lxml')
        productName = contentHtml.find('h1', {'class': 'productPage_title__1B1Yw'}).get_text(strip = True)
        productPrice = contentHtml.find('span', {'class': 'PriceBlock_price__3hwFe'}).get_text(strip = True).replace('\xa0', '')[:-1]
        specificationsHtml = contentHtml.find('div', {'class': 'Grid_row__ZvFHa productPage_bottom__2rdYu'}).find_all('li', {'class': 'CharacteristicsItem_li__hJ4YF'})
        specifications = []
        for item in specificationsHtml:
            try:
                name = item.find('div', {'class': 'CharacteristicsItem_name__-AhRC'}).find('span').get_text(strip = True)
                value = item.find('p', {'class': 'CharacteristicsItem_value__3-EWJ'}).find('span').get_text(strip = True)
                specifications.append({'name': name, 'value': value})
            except Exception as e:
                continue
        res = {
            'name': productName,
            'price': productPrice,
            'url': url,
            'specifications': specifications,
        }
    except Exception as e:
        return None
    return res

def getData(driver, query):
    """Функция поиска по сайту"""

    browser = driver.getBrowser()
    browser.get(f"https://www.regard.ru/catalog?search={query}")
    currentUrl = browser.current_url
    if 'search' in currentUrl or 'catalog' in currentUrl:
        try:
            WebDriverWait(browser, timeout=5).until(ec.visibility_of_element_located((By.CLASS_NAME, 'rendererWrapper')))
        except Exception as e:
            return None
        grid = browser.find_element(By.CLASS_NAME, 'rendererWrapper')
        soup = BeautifulSoup(grid.get_attribute('innerHTML'), 'lxml')
        elements = soup.find_all('div', {'class': 'Card_wrap__2fsLE'})
        for element in elements:
            try:
                productName = element.find('a', {'class': 'CardText_link__2H3AZ'}).get_text(strip = True)
                productPrice = element.find('span', {'class': 'CardPrice_price__1t0QB'}).get_text(strip=True).replace("\xa0", "")[:-1]
                link = f"https://www.regard.ru{element.find('a', {'class': 'CardText_link__2H3AZ'}).get('href')}"
            except Exception as e:
                continue
            yield {
                'name': productName,
                'price': productPrice,
                'url': f'{link}'
            }
    elif 'product' in currentUrl:
        res = parseProductCard(browser, currentUrl)
        if res:
            yield {
                'name': res.get('name'),
                'price': res.get('price'),
                'url': currentUrl
            }

def search(driver, query):
    """Функция поиска по сайту"""
    return searchProcessing(driver, query, getData)
