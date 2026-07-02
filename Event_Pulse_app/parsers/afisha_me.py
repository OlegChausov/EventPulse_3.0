
from datetime import date
import requests
from bs4 import BeautifulSoup

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


HEADERS = {"User-Agent": "Mozilla/5.0"}



async def get_afisha_me_films(
        start_date: date ,
        end_date: date) -> list[dict]:


    URL = f"https://afisha.me/day/film/{start_date}/{end_date}/"
    response = requests.get(URL, headers=HEADERS, verify=False)
    response.raise_for_status()  # Чтобы не продолжать парсить страницу, если она не загрузилась.

    soup = BeautifulSoup(response.text, "html.parser")
    film_links = []
    seen_urls = set()

    for a_tag in soup.find_all("a", class_="name"):
        href = a_tag.get("href", "")
        if href.startswith("https://afisha.me/film/") and href not in seen_urls:
            title = a_tag.get_text(strip=True)
            film_links.append({"event_type": "film", "title": title, "url": href})
            seen_urls.add(href)

    return film_links

