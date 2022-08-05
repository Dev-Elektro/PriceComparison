# -*- coding: utf-8 -*-
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from bs4 import BeautifulSoup

def verified(txt, query):
    v = 0
    for i in query.split(" "):
        if i.lower() in txt.lower():
            v += 1
    if len(query.split(" ")) - v != 0:
        return False
    return True

def parseProductCard(driver, url):
    try:
        driver.get(f"{url}properties/")
        WebDriverWait(driver, timeout=10).until(ec.visibility_of_element_located((By.CLASS_NAME, 'SpecificationsFull')))
        contentHtml = driver.find_element(By.ID, 'content').get_attribute('innerHTML')
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
    driver.get(f"https://www.citilink.ru/search/?text={query}&sorting=price_asc")
    currentUrl = driver.current_url
    if 'search' in currentUrl:
        try:
            WebDriverWait(driver, timeout=10).until(ec.visibility_of_element_located((By.CLASS_NAME, 'ProductCardCategoryList__grid')))
        except Exception as e:
            return None

        grid = driver.find_element(By.CLASS_NAME, 'ProductCardCategoryList__grid')
        soup = BeautifulSoup(grid.get_attribute('innerHTML'), 'lxml')
        elements = soup.find_all('div', {'class': 'ProductCardVertical'})
        for element in elements:
            try:
                productName = element.find('a', {'class': 'ProductCardVertical__name'}).get('title')
                productPrice = element.find('span', {'class': 'ProductCardVerticalPrice__price-current_current-price'}).get_text(strip=True).replace(" ", "")
                link = f"https://www.citilink.ru{element.find('a', {'class': 'ProductCardVertical__name'}).get('href')}"
            except Exception as e:
                continue
            if not verified(productName, query):
                res = parseProductCard(driver, link)
                if not res:
                    continue
                buf = f"{' '.join(map(lambda x: str(x.get('value')), res.get('specifications')))} {res.get('name')}"
                if not verified(buf, query):
                    continue
            yield {
                'name': productName,
                'price': productPrice,
                'url': f'{link}'
            }
    elif 'product' in currentUrl:
        res = parseProductCard(driver, currentUrl)
        if res:
            buf = f"{' '.join(map(lambda x: str(x.get('value')), res.get('specifications')))} {res.get('name')}"
            if verified(buf, query):
                yield {
                    'name': res.get('name'),
                    'price': res.get('price'),
                    'url': currentUrl
                }
