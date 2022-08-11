# -*- coding: utf-8 -*-
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from bs4 import BeautifulSoup
from . import verified, verifiedSpec

def parseProductCard(browser, url):
    """Разбор страницы товара с характеристиками"""

    try:
        browser.get(f"{url}properties/")
        # Ожидание загрузки всех ajax-запросов
        WebDriverWait(browser, timeout=5).until(ec.visibility_of_element_located((By.CLASS_NAME, 'SpecificationsFull')))
        contentHtml = browser.find_element(By.ID, 'content').get_attribute('innerHTML')
        contentHtml = BeautifulSoup(contentHtml, 'lxml')
        productName = contentHtml.find('h1', {'class': 'ProductHeader__title'}).get_text(strip = True)
        productPrice = contentHtml.find('span', {'class': 'ProductHeader__price-default_current-price'}).get_text(strip = True).replace(' ', '')
        specificationsHtml = contentHtml.find('div', {'class': 'TabContent'}).find_all('div', {'class': 'Specifications__row'})
        specifications = []
        for item in specificationsHtml:
            try:
                name = item.find('div', {'class': 'Specifications__column_name'}).get_text(strip = True)
                value = item.find('div', {'class': 'Specifications__column_value'}).get_text(strip = True)
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

def search(driver, query):
    """Функция поиска по сайту"""

    browser = driver.getBrowser()
    browser.get(f"https://www.citilink.ru/search/?text={query}")
    currentUrl = browser.current_url
    if 'search' in currentUrl:
        try:
            WebDriverWait(browser, timeout=5).until(ec.visibility_of_element_located((By.CLASS_NAME, 'ProductCardCategoryList__grid')))
        except Exception as e:
            return None

        grid = browser.find_element(By.CLASS_NAME, 'ProductCardCategoryList__grid')
        soup = BeautifulSoup(grid.get_attribute('innerHTML'), 'lxml')
        elements = soup.find_all('div', {'class': 'ProductCardVertical'})
        for element in elements:
            try:
                productName = element.find('a', {'class': 'ProductCardVertical__name'}).get('title')
                productPrice = element.find('span', {'class': 'ProductCardVerticalPrice__price-current_current-price'}).get_text(strip=True).replace(" ", "")
                link = f"https://www.citilink.ru{element.find('a', {'class': 'ProductCardVertical__name'}).get('href')}"
            except Exception as e:
                continue
            ver = verified(productName, query)
            if ver == 0:
                continue
            elif ver < 100:
                res = parseProductCard(browser, link)
                if not res:
                    continue
                if verifiedSpec(res.get('name'), res.get('specifications'), query) == 0:
                    continue
            yield {
                'name': productName,
                'price': productPrice,
                'url': f'{link}'
            }
    elif 'product' in currentUrl:
        res = parseProductCard(browser, currentUrl)
        if res:
            if verifiedSpec(res.get('name'), res.get('specifications'), query) == 100:
                yield {
                    'name': res.get('name'),
                    'price': res.get('price'),
                    'url': currentUrl
                }
