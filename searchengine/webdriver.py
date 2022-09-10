import os
from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import sys
from subprocess import CREATE_NO_WINDOW


class Driver:
    """Selenium драйвер с настройкой скрытия автоматизации.
    Принимает значение headless = False для отображения окна браузера."""

    def __init__(self, headless: bool = True):
        self.driver = None
        self.options = Options()
        if headless:
            self.options.add_argument("--headless")
        self.options.add_argument("start-maximized")
        self.options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        path = os.path.abspath(os.getcwd())
        if getattr(sys, 'frozen', False):
            path = sys._MEIPASS
        path = os.path.join(path, "chrome-win/chrome.exe")
        self.options.binary_location = path
        self.s = Service('chromedriver.exe')
        self.s.creationflags = CREATE_NO_WINDOW

    def start(self):
        """Запуск драйвера и браузера."""
        self.driver = webdriver.Chrome(service=self.s, options=self.options)
        # Активация режима скрытия автоматизации
        stealth(
            self.driver,
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
