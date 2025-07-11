import cloudscraper
from bs4 import BeautifulSoup
import json
import os
from tqdm.auto import tqdm

scraper = cloudscraper.create_scraper()


def crawl_sticker(id):
    url = f"https://store.line.me/stickershop/product/{id}/en"

    response = scraper.get(url)

    soup = BeautifulSoup(response.text, "html.parser")

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

    return item


def crawl_emoji(id):
    url = f"https://store.line.me/emojishop/product/{id}/en"

    response = scraper.get(url)

    soup = BeautifulSoup(response.text, "html.parser")

    thumb = soup.find("div", {"data-widget-id": "MainSticon"}).get("data-preview")
    thumb = json.loads(thumb)

    name = soup.find("p", {"data-test": "emoji-name-title"}).text.strip()
    author = soup.find("a", {"data-test": "emoji-author"}).text.strip()

    div = soup.find("div", {"data-widget-id": "StickerPreview"})

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

    return item


def crawl_shop(page=1):
    OUT = "extension/data/line_stickers.jsonl"
    ids = set()
    items = []
    if os.path.exists(OUT):
        with open(OUT, "r") as f:
            items = [json.loads(line) for line in f]
            ids = set([x["id"] for x in items])

    for page in tqdm(range(1, 36)):
        url = f"https://store.line.me/stickershop/showcase/top/en?page={page}"
        response = scraper.get(url)

        soup = BeautifulSoup(response.text, "html.parser")
        ul = soup.find("ul", class_="mdCMN02Ul")
        spans = ul.select("a")

        for span in tqdm(spans, desc=f"Page {page}"):
            pack_url = span.get("href")
            # img = span.find("img")
            # thumb = img.get("src")
            # name = img.get("alt")
            id = pack_url.split("/")[-2]

            print(id, pack_url)
            if id in ids:
                continue

            item = crawl_sticker(id)
            ids.add(id)

            items.append(item)
            with open(OUT, "a") as f:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

    return items


def crawl_single(id):
    OUT = "extension/data/line.json"
    items = []
    ids = set()

    if os.path.exists(OUT):
        with open(OUT, "r") as f:
            items = json.load(f)
            ids = set([x["id"] for x in items])

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


if __name__ == "__main__":
    id = "35621"
    id = "32228"
    id = "618c9548801cfd4492efadcb"
    id = "27642"
    id = "17993"
    id = "875"
    id = "835"
    # crawl_single(id)
    crawl_shop()
