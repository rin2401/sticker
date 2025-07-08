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


async def sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.message.text
    print("Q:", q)

    q = q.lower().strip()

    if q in M:
        ss = M[q]["stickers"]
        s = random.choice(ss)
        await update.message.reply_sticker(s["id"])
    else:
        for k in M:
            if q in k.split():
                ss = M[k]["stickers"]
                s = random.choice(ss)
                await update.message.reply_sticker(s["id"])
                return

        for k in M:
            if q in k:
                ss = M[k]["stickers"]
                s = random.choice(ss)
                await update.message.reply_sticker(s["id"])
                return

        await update.message.reply_text("Không tìm thấy sticker.")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"Hi {update.effective_user.display_name}")


if __name__ == "__main__":
    app = ApplicationBuilder().token(os.getenv("TOKEN")).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, sticker))
    print("🤖 Bot đang chạy...")
    app.bot.delete_webhook()
    app.run_polling()
