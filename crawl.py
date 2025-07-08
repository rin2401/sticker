import requests
import json
from tqdm.auto import tqdm
import os
import asyncio
import httpx

client = httpx.AsyncClient()


async def get_sticker():
    OUT = "data/sticker.json"
    if os.path.exists(OUT):
        with open(OUT, "r") as f:
            return json.load(f)

    url = "https://stickers.zaloapp.com/sticker"
    response = await client.get(url)

    stickers = response.json()["value"]["all"]

    for s in tqdm(stickers):
        s["stickers"] = await get_cate_sticker(s["id"])

    with open(OUT, "w") as f:
        f.write(json.dumps(stickers, indent=4, ensure_ascii=False))

    return stickers


async def get_cate_sticker(cid):
    url = f"https://stickers.zaloapp.com/cate-stickers?cid={cid}"
    response = await client.get(url)

    return response.json()["value"]


async def get_sticker_img(cid, sticker_id, url):
    OUT = f"data/img/{cid}/{sticker_id}.png"
    if os.path.exists(OUT):
        return

    os.makedirs(f"data/img/{cid}", exist_ok=True)
    response = await client.get(url)

    with open(OUT, "wb") as f:
        f.write(response.content)


async def main():
    stickers = await get_sticker()
    for s in tqdm(stickers):
        tasks = [
            get_sticker_img(s["id"], sticker["id"], sticker["url"])
            for sticker in s["stickers"]
        ]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
