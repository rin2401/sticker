import httpx
import json
import random
import os
from zalo_bot import Update
from zalo_bot.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from dotenv import load_dotenv

load_dotenv()

client = httpx.AsyncClient()

with open("data/sticker.json") as f:
    data = json.load(f)

M = {d["name"].lower().strip(): d for d in data}


async def search_pack(q):
    q = q.lower().strip()

    if q in M:
        return M[q]["stickers"]

    for k in M:
        if q in k.split():
            return M[k]["stickers"]

    for k in M:
        if q in k:
            return M[k]["stickers"]


async def search_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.message.text
    print("Q:", q)

    ss = await search_pack(q)
    if ss:
        s = random.choice(ss)
        await update.message.reply_sticker(s["id"])
    else:
        await update.message.reply_text("Không tìm thấy sticker.")


def get_sticker_by_id(sid):
    for ss in data:
        for sticker in ss["stickers"]:
            if sid in sticker["url"] or sticker["id"] == sid:
                return sticker


def get_sticker_random():
    s = random.choice(data)
    ss = s["stickers"]
    return random.choice(ss)


async def get_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    s = None
    if context.args:
        s = get_sticker_by_id(context.args[0])
        if not s:
            await update.message.reply_text("Không tìm thấy sticker.")
            return
    else:
        s = get_sticker_random()

    await update.message.reply_sticker(s["id"])


if __name__ == "__main__":
    app = ApplicationBuilder().token(os.getenv("TOKEN")).build()

    app.add_handler(CommandHandler("s", get_sticker))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_sticker))
    app.add_handler(MessageHandler(filters.STICKER & ~filters.COMMAND, get_sticker))

    print("🤖 Bot đang chạy...")
    app.bot.delete_webhook()
    app.run_polling()
