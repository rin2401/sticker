import cloudscraper
from bs4 import BeautifulSoup
import json
import os

scraper = cloudscraper.create_scraper()


def crawl_pack(id):
    url = f"https://combot.org/stickers/{id}"

    response = scraper.get(url)

    soup = BeautifulSoup(response.text, "html.parser")

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

    print(json.dumps(item, indent=4, ensure_ascii=False))

    return item


if __name__ == "__main__":
    OUT = "extension/data/tele.json"
    items = []
    ids = set()

    if os.path.exists(OUT):
        with open(OUT, "r") as f:
            items = json.load(f)
            ids = set([x["id"] for x in items])

    id = "utyaduck"
    id = "Hamsters_Stickers"
    if id in ids:
        print("Exist pack id")
        exit()

    item = crawl_pack(id)
    items.append(item)

    with open(OUT, "w") as f:
        f.write(json.dumps(items, indent=4, ensure_ascii=False))
