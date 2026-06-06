import os
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
GEMINI_KEY = os.environ["GEMINI_KEY"]

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
user_histories = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Salom! Men AI botman!\n"
        "Savolingizni bering 😊\n"
        "/clear — suhbatni tozalash"
    )

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_histories[update.effective_user.id] = []
    await update.message.reply_text("✅ Suhbat tozalandi!")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text
    if uid not in user_histories:
        user_histories[uid] = []
    await context.bot.send_chat_action(update.effective_chat.id, "typing")
    user_histories[uid].append({"role": "user", "parts": [text]})
    if len(user_histories[uid]) > 20:
        user_histories[uid] = user_histories[uid][-20:]
    try:
        chat = model.start_chat(history=user_histories[uid][:-1])
        resp = chat.send_message(text)
        reply = resp.text
        user_histories[uid].append({"role": "model", "parts": [reply]})
        await update.message.reply_text(reply)
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("❌ Xatolik yuz berdi.")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
