import requests
from bs4 import BeautifulSoup
from datetime import date
import re
import time


HEADERS = {"User-Agent": "Mozilla/5.0"}


def extract_events(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    events = []
    for a_tag in soup.select("a[href^='/event/']"):
        title = a_tag.text.strip()
        relative_url = a_tag.get("href")
        full_url = f"https://concertful.com{relative_url}"
        events.append({"event_type": "concert", "location": "Warshaw", 'title': title, 'url': full_url})
    return events

def get_total_pages(html: str) -> int:
    soup = BeautifulSoup(html, "html.parser")
    counter = soup.select_one(".buttons_counter span")
    if counter:
        match = re.search(r"Page\s+\d+\s+of\s+(\d+)", counter.text)
        if match:
            return int(match.group(1))
    return 1

async def get_concertful_pl(start_date: date) -> list[dict]:
    all_events = []
    seen_urls = set()

    # ✅ Получаем первую страницу для определения количества
    first_url = f"https://concertful.com/area/poland/warsaw?from={start_date}&category=&order=event_date&page=1"
    response = requests.get(first_url, headers=HEADERS)
    html = response.text
    total_pages = get_total_pages(html)

    for page in range(1, total_pages + 1):
        url = f"https://concertful.com/area/poland/warsaw?from={start_date}&category=&order=event_date&page={page}"
        response = requests.get(url, headers=HEADERS)
        html = response.text
        events = extract_events(html)

        for event in events:
            if event['url'] not in seen_urls:
                all_events.append(event)
                seen_urls.add(event['url'])

        time.sleep(1)  # ⏳ пауза между запросами


    return all_events


