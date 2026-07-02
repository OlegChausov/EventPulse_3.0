from datetime import date, timedelta
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

async def get_biletai_lt_concerts(start_date: date, end_date: date) -> list[dict]:
    # 1. Исправляем формат даты на YYYY-MM-DD
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")

    url = f"https://www.bilietai.lt/en/tickets/music?date={start_str}&date={end_str}&sortOrder=date_asc&page=1"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    

    # Вложенная функция (исправили отступы внутри неё)
    def detect_last_page(soup_obj) -> int:
        pages = []
        
        # 1. Ищем родительский контейнер пагинации по его характерным классам
        pagination_div = soup_obj.find("div", class_=lambda x: x and "flex" in x and "items-center" in x and "gap-1" in x)
        
        if pagination_div:
            # 2. Находим все span элементы внутри этого контейнера
            for span in pagination_div.find_all("span"):
                txt = span.get_text(strip=True).replace("\xa0", "")
                # Проверяем, является ли текст числом (чтобы проигнорировать многоточие "…")
                if txt.isdigit():
                    pages.append(int(txt))
                    
        # 3. Возвращаем максимальное найденное число (14), либо 1, если ничего не нашли
        return max(pages) if pages else 1

    # Исправили имя вызываемой функции на detect_last_page
    last_page = detect_last_page(soup)

    concerts = []
    seen_concerts = set()

    for page in range(1, last_page + 1):
        actual_url = f"https://www.bilietai.lt/en/tickets/music?date={start_str}&date={end_str}&sortOrder=date_asc&page={page}"
        if page > 1:
            response = requests.get(actual_url, headers=HEADERS)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

        # 2. Обновленный селектор для карточек (ищем теги 'a' с классом 'card')
        for a_tag in soup.find_all("a", class_=lambda x: x and "card" in x):
            # Заголовок обычно лежит в теге h3 или h4 внутри карточки
            title_tag = a_tag.find(["h3", "h4"])
            title = title_tag.get_text(strip=True) if title_tag else ""
            url = a_tag.get("href", "")

            # Делаем ссылку абсолютной, если она относительная
            if url and not url.startswith("http"):
                url = "https://www.bilietai.lt" + url

            if title and url and url not in seen_concerts:
                concerts.append(
                    {"event_type": "concert", "location": "Vilnius", "title": title, "url": url}
                )
                seen_concerts.add(url)

    return concerts

