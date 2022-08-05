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
        driver.get(url)
        WebDriverWait(driver, timeout=10).until(ec.visibility_of_element_located((By.ID, 'section-characteristics')))
        contentHtml = driver.find_element(By.ID, 'layoutPage').get_attribute('innerHTML')
        contentHtml = BeautifulSoup(contentHtml, 'lxml')
        productName = contentHtml.find('div', {'data-widget': 'webProductHeading'}).get_text(strip = True)
        container = contentHtml.find('div', {'class': 'container', 'data-widget': 'container'})
        productPrice = container.find('div', {'slot': 'content'}).find('span').get_text(strip = True).replace('\u2009', '')[:-1]
        specificationsHtml = contentHtml.find('div', {'id': 'section-characteristics'}).find_all('div', recursive = False)[1].find_all('dl')
        specifications = []
        for item in specificationsHtml:
            try:
                name = item.find('dt').find('span').get_text(strip = True)
                value = item.find('dd').get_text(strip = True)
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
    driver.get(f"https://www.ozon.ru/search/?text={query}")
    currentUrl = driver.current_url
    if 'search' in currentUrl or 'category' in currentUrl:
        try:
            WebDriverWait(driver, timeout=10).until(ec.visibility_of_element_located((By.CSS_SELECTOR, '.widget-search-result-container')))
        except Exception as e:
            return None
        grid = driver.find_element(By.CSS_SELECTOR, '.widget-search-result-container')
        soup = BeautifulSoup(grid.get_attribute('innerHTML'), 'lxml')
        elements = soup.find('div').find_all('div', recursive = False)
        for element in elements:
            if 'category' in currentUrl:
                try:
                    body = element.find_all('div', recursive = False)
                    productName = body[1].find('a').get_text(strip = True)
                    p = body[2].find_all('div', recursive = False)
                    if len(p) == 2:
                        productPrice = p[0].find('span').get_text(strip=True).replace("\u2009", "")[:-1]
                    else:
                        productPrice = p[1].find('span').get_text(strip=True).replace("\u2009", "")[:-1]
                    link = f"https://www.ozon.ru{body[1].find('a').get('href')}"
                except Exception as e:
                    continue
            else:
                try:
                    productName = element.find('div', recursive = False).find('a').get_text(strip = True)
                    p = element.find('div', recursive = False).find_all('div', recursive = False)
                    if len(p) == 2:
                        productPrice = p[0].find('span').get_text(strip=True).replace("\u2009", "")[:-1]
                    else:
                        productPrice = p[1].find('span').get_text(strip=True).replace("\u2009", "")[:-1]
                    link = f"https://www.ozon.ru{element.find('div', recursive = False).find('a').get('href')}"
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
