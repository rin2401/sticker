import cloudscraper
from bs4 import BeautifulSoup
import json
import os

scraper = cloudscraper.create_scraper()


def crawl_pack(id):
    url = f"https://store.line.me/stickershop/product/{id}/en"

    response = scraper.get(url)

    soup = BeautifulSoup(response.text, "html.parser")

    thumb = soup.find("div", {"data-widget-id": "MainSticker"}).get("data-preview")
    thumb = json.loads(thumb)

    spans = soup.find_all("li", {"data-test": "sticker-item"})

    stickers = []
    for span in spans:
        d = json.loads(span.get("data-preview"))
        stickers.append(
            {
                "id": d["id"],
                "url": d["staticUrl"],
            }
        )

    name = soup.find("p", {"data-test": "sticker-name-title"}).text.strip()
    author = soup.find("a", {"data-test": "sticker-author"}).text.strip()

    item = {
        "textUploader": author,
        "qrCode": "",
        "price": "Miễn phí",
        "name": name,
        "thumbImg": thumb["staticUrl"],
        "iconUrl": thumb["staticUrl"],
        "id": id,
        "source": "line",
        "totalImage": f"{len(stickers)} sticker",
        "stickers": stickers,
    }

    print(json.dumps(item, indent=4, ensure_ascii=False))

    return item


if __name__ == "__main__":
    OUT = "extension/data/line.json"
    items = []
    ids = set()

    if os.path.exists(OUT):
        with open(OUT, "r") as f:
            items = json.load(f)
            ids = set([x["id"] for x in items])

    id = "35621"
    id = "32228"
    if id in ids:
        print("Exist pack id")
        exit()

    item = crawl_pack(id)
    items.append(item)

    with open(OUT, "w") as f:
        f.write(json.dumps(items, indent=4, ensure_ascii=False))
