from re import S
import cloudscraper
from bs4 import BeautifulSoup
import json
import os

scraper = cloudscraper.create_scraper()


def crawl_sticker(id):
    url = f"https://store.line.me/stickershop/product/{id}/en"

    response = scraper.get(url)

    soup = BeautifulSoup(response.text, "html.parser")
    print(soup.prettify())

    thumb = soup.find("div", {"data-widget-id": "MainSticker"}).get("data-preview")
    thumb = json.loads(thumb)

    name = soup.find("p", {"data-test": "sticker-name-title"}).text.strip()
    author = soup.find("a", {"data-test": "sticker-author"}).text.strip()

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


def crawl_emoji(id):
    url = f"https://store.line.me/emojishop/product/{id}/en"

    response = scraper.get(url)

    soup = BeautifulSoup(response.text, "html.parser")
    print(soup.prettify())

    thumb = soup.find("div", {"data-widget-id": "MainSticon"}).get("data-preview")
    thumb = json.loads(thumb)

    name = soup.find("p", {"data-test": "emoji-name-title"}).text.strip()
    author = soup.find("a", {"data-test": "emoji-author"}).text.strip()

    div = soup.find("div", {"data-widget-id": "StickerPreview"})
    print(div.prettify())

    spans = div.select('li[class*="FnStickerPreviewItem"]')
    stickers = []
    for span in spans:
        d = json.loads(span.get("data-preview"))
        stickers.append(
            {
                "id": d["id"],
                "url": d["staticUrl"],
            }
        )
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
    id = "618c9548801cfd4492efadcb"
    id = "27642"
    if id in ids:
        print("Exist pack id")
        exit()

    if id.isnumeric():
        item = crawl_sticker(id)
    else:
        item = crawl_emoji(id)

    items.append(item)

    with open(OUT, "w") as f:
        f.write(json.dumps(items, indent=4, ensure_ascii=False))
