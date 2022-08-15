from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

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

def verified(txt, query):
    """Пословестный поиск совподений в строке."""
    queryItems = query.split(" ") # Разбивка поискового запроса на слова.
    # Возврат True если все слова поискового запроса нашлись в тексте.
    return sum(True for i in queryItems if i.lower() in txt.lower()) * 100 / len(queryItems)

def verifiedSpec(name, spec, query):
    """Пословестный поиск совпадений в характеристиках."""
    # Сбор всех характеристик в одну строку
    buf = f"{' '.join(map(lambda x: str(x.get('value')), spec))} {name}"
    return verified(buf, query)
