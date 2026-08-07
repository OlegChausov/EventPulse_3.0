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
    
    # Добавьте эти три строки:
    options.add_argument("--disable-gpu")
    options.add_argument("--no-zygote")
    options.add_argument("--remote-debugging-port=9222")
    # Используем 0 вместо 9222, чтобы Chrome сам выбирал свободный порт
    options.add_argument("--remote-debugging-port=0")


    service = None

    if sys.platform.startswith("win"):
        path = os.environ.get("CHROMEDRIVER_PATH")
        print(f"🔧 [FACTORY] CHROMEDRIVER_PATH из env: {path}", flush=True)
        if not path:
            from webdriver_manager.chrome import ChromeDriverManager
            path = ChromeDriverManager().install()
        service = Service(path)
    else:
        linux_path = os.environ.get("CHROMEDRIVER_PATH", "/usr/bin/chromedriver")
        if os.path.exists(linux_path):
            service = Service(linux_path)
        else:
            service = Service()

    return webdriver.Chrome(service=service, options=options)