# relax_by.py

from bs4 import BeautifulSoup
import time as t
from Event_Pulse_app.utils.webdriver_factory import get_chrome_driver




HEADERS = {"User-Agent": "Mozilla/5.0"}


async def get_relax_by_films() -> list[dict]:
    """
    Аналог get_afisha_me_films, но для relax.by.
    """

    url = "https://afisha.relax.by/kino/minsk/"

    driver = get_chrome_driver()
    driver.get(url)

    # Скроллим до конца страницы
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        t.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, "html.parser")
    film_links = []
    seen_urls = set()

    # Ищем ссылки вида /kino/<число>-<slug>/minsk/
    for a in soup.select('a[href*="/kino/"]'):
        href = a.get("href") or ""
        if "/kino/" in href:
            part = href.split("/kino/")[1]
            if part and part[0].isdigit():  # фильм имеет числовой ID
                title = ""
                img = a.select_one("img") or a.find_previous("img") or a.find("img")
                if img:
                    alt = img.get("alt") or ""
                    if alt.strip():
                        title = alt.strip()

                if not title:
                    continue

                if href not in seen_urls:
                    film_links.append({
                        "event_type": "film",
                        "title": title,
                        "url": href
                    })
                    seen_urls.add(href)

    return film_links
