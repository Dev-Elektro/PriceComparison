from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

class Driver():
    def __init__(self, headless = True):
        self.options = Options()
        if headless:
            self.options.add_argument("--headless")
        self.options.add_argument("start-maximized")
        self.options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)

        self.s = Service('chromedriver.exe')

    def start(self):
        self.driver = webdriver.Chrome(service = self.s, options = self.options)

        stealth(self.driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )

    def stop(self):
        self.driver.quit()

    def getBrowser(self):
        return self.driver

def verified(txt, query):
    queryItems = query.split(" ")
    return not len(queryItems) - sum(True for i in queryItems if i.lower() in txt.lower())

def verifiedSpec(name, spec, query):
    buf = f"{' '.join(map(lambda x: str(x.get('value')), spec))} {name}"
    return verified(buf, query)
