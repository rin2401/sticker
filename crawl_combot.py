import cloudscraper
from bs4 import BeautifulSoup
import json

scraper = cloudscraper.create_scraper()


id = "utyaduck"
url = f"https://combot.org/stickers/{id}"


response = scraper.get(url)

soup = BeautifulSoup(response.text, "html.parser")

print(soup.prettify())
res = soup.find_all("div", class_="lozad")
res = [r.get("data-src") for r in res]

name = soup.find("h3", class_="tw-text-lg").get_text().strip()

item = {
    "textUploader": "Họa sĩ",
    "qrCode": "",
    "price": "Miễn phí",
    "name": name,
    "thumbImg": res[0],
    "iconUrl": res[0],
    "id": id,
    "source": "Combot",
    "totalImage": f"{len(res)} sticker",
    "stickers": [
        {
            "id": f"{id}_{i}",
            "url": url,
        }
        for i, url in enumerate(res)
    ],
}

print(item)

with open("extension/data/tele.json", "w") as f:
    f.write(json.dumps([item], indent=4, ensure_ascii=False))
