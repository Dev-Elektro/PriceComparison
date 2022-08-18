# -*- coding: utf-8 -*-
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from bs4 import BeautifulSoup
from . import searchProcessing

def parseProductCard(browser, url):
    """Разбор страницы товара с характеристиками"""

    try:
        browser.get(f"{url}characteristics/")
        WebDriverWait(browser, timeout=5).until(ec.visibility_of_element_located((By.CLASS_NAME, 'product-card-description')))
        WebDriverWait(browser, timeout=5).until(ec.visibility_of_element_located((By.CLASS_NAME, 'product-buy__price')))
        contentHtml = browser.find_element(By.CSS_SELECTOR, '.container.product-card').get_attribute('innerHTML')
        contentHtml = BeautifulSoup(contentHtml, 'lxml')
        if contentHtml.find('div', {'class': 'order-avail-wrap order-avail-wrap_not-avail'}):
            return None
        productName = contentHtml.find('h1', {'class': 'product-card-top__title'}).get_text(strip = True).replace('Характеристики ', '')
        productPrice = contentHtml.find('div', {'class': 'product-buy__price'}).get_text(strip = True).replace(' ', '')[:-1]
        specificationsHtml = contentHtml.find('div', {'class': 'product-card-description'}).find_all('div', {'class': 'product-characteristics__spec'})
        specifications = []
        for item in specificationsHtml:
            try:
                name = item.find('div', {'class': 'product-characteristics__spec-title'}).get_text(strip = True)
                value = item.find('div', {'class': 'product-characteristics__spec-value'}).get_text(strip = True)
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
    browser = driver.getBrowser()
    browser.get(f"https://www.dns-shop.ru/search/?q={query}")
    currentUrl = browser.current_url
    if 'search' in currentUrl or 'catalog' in currentUrl:
        try:
            WebDriverWait(browser, timeout=5).until(ec.visibility_of_element_located((By.CLASS_NAME, 'products-list__content')))
            WebDriverWait(browser, timeout=5).until(ec.visibility_of_element_located((By.CLASS_NAME, 'product-buy__price-wrap')))
            WebDriverWait(browser, timeout=5).until(ec.visibility_of_element_located((By.CLASS_NAME, 'order-avail-wrap')))
        except Exception as e:
            return None

        grid = browser.find_element(By.CLASS_NAME, 'products-list')
        soup = BeautifulSoup(grid.get_attribute('innerHTML'), 'lxml')
        elements = soup.find_all('div', {'class': 'catalog-product'})
        for element in elements:
            try:
                productName = element.find('a', {'class': 'catalog-product__name'}).get_text(strip = True)
                productPrice = element.find('div', {'class': 'product-buy__price'}).get_text(strip=True).replace(" ", "")[:-1]
                availability = False if 'Товара нет в наличии' in element.find('div', {'class': 'order-avail-wrap'}).get_text(strip=True) else True
                link = f"https://www.dns-shop.ru{element.find('a', {'class': 'catalog-product__name'}).get('href')}"
            except Exception as e:
                continue
            if not availability:
                continue
            yield {
                'name': productName,
                'price': productPrice,
                'url': f'{link}',
                'specifications': None
            }
    elif 'product' in currentUrl:
        res = parseProductCard(browser, currentUrl)
        if res:
            yield {
                'name': res.get('name'),
                'price': res.get('price'),
                'url': currentUrl,
                'specifications': res.get('specifications')
            }

def search(driver, query):
    """Функция поиска по сайту"""
    return searchProcessing(driver, query, getData)
