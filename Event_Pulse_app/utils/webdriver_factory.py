# webdriver_factory.py нужен только для windows
import os
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

def get_chrome_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    if sys.platform.startswith("win"):
        path = os.environ.get("CHROMEDRIVER_PATH")
        print(f"🔧 [FACTORY] CHROMEDRIVER_PATH из env: {path}", flush=True)
        if not path:
            from webdriver_manager.chrome import ChromeDriverManager
            path = ChromeDriverManager().install()
        service = Service(path)

    return webdriver.Chrome(service=service, options=options)