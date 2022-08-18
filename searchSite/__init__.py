from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import re

class Driver():
    """Selenium драйвер с настройкой скрытия автоматизации.
    Принимает значение headless = False для отображения окна браузера."""

    def __init__(self, headless = True):
        self.options = Options()
        if headless:
            self.options.add_argument("--headless")
        self.options.add_argument("start-maximized")
        self.options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.options.binary_location = "chrome-win/chrome.exe"
        self.s = Service('chromedriver.exe')

    def start(self):
        """Запуск драйвера и браузера."""
        self.driver = webdriver.Chrome(service = self.s, options = self.options)
        # Активация режима скрытия автоматизации
        stealth(self.driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )

    def stop(self):
        """Остановка драйвера и закрытие браузера."""
        self.driver.quit()

    def getBrowser(self):
        """Возврат объекта драйвера"""
        return self.driver

def wordProcessing(query):
    txt = query.lower().strip()+'\n'
    stopWord = [r'lcd']
    for word in stopWord:
        txt = re.sub(word, '', txt)
    regex = r"([-\da-zA-Z]{2,})[\s|\n]"
    matches = re.findall(regex, txt, re.MULTILINE | re.UNICODE)
    model_pos = 0
    for p, x in enumerate(matches):
        lenW = len(re.findall(r'[a-z]', x))
        lenD = len(re.findall(r'\d', x))
        if lenW > 0 and lenD > 0:
            model_pos = p
            break
    if model_pos > 0:
        model_pos = model_pos - 1 if model_pos == 1 else model_pos - 2
    queryLine = ''
    for x, word in enumerate(matches[model_pos:]):
        queryLine += f"{word.strip()} "
        if len(matches[model_pos:]) == 1:
            yield queryLine.strip()
        if x > 0:
            yield queryLine.strip()

def searchProcessing(driver, query, getData):
    if partNumber := re.findall(r'\[([\w-]+)\]', query): # Проверка наличия парт номера выделенного [] скобками в запросе
        for item in getData(driver, partNumber[0]): # Получаем поисковый ответ от сайта
            buf = item.get('name')
            if spec := item.get('specifications'): # Если в результате поика есть спецификации, то их собираем в строку
                buf += f"{' '.join(map(lambda x: str(x.get('value')), spec))}"
            if partNumber[0] in buf: # Проверка совподает ли парт номер с результатом поска
                yield item
        return
    # Если в запросе нету парт номера выполняем текстовый поиск.
    for query_proc in wordProcessing(query):
        emptyData = True
        interationStop = False
        for item in getData(driver, query_proc):
            emptyData = False
            regex = r"[\w-]{3,}"
            buf = item.get('name')
            if spec := item.get('specifications'):
                buf += f"{' '.join(map(lambda x: str(x.get('value')), spec))}"
            query_word = re.findall(regex, query.lower(), re.MULTILINE | re.UNICODE)
            result_word = re.findall(regex, buf.lower(), re.MULTILINE | re.UNICODE)
            overlap = sum(True for word in query_word if word in result_word)
            if overlap == len(query_word):
                interationStop = True
                yield item
        if emptyData or interationStop:
            return
