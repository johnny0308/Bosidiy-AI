import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
GEMINI_KEY = os.environ["GEMINI_KEY"]

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
user_histories = {}

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Salom! Men AI botman. Savolingizni bering!\n/clear — suhbatni tozalash")

async def clear(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_histories[update.effective_user.id] = []
    await update.message.reply_text("✅ Tozalandi!")

async def handle(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text
    if uid not in user_histories:
        user_histories[uid] = []
    await ctx.bot.send_chat_action(update.effective_chat.id, "typing")
    user_histories[uid].append({"role": "user", "parts": [text]})
    try:
        chat = model.start_chat(history=user_histories[uid][:-1])
        resp = chat.send_message(text)
        reply = resp.text
        user_histories[uid].append({"role": "model", "parts": [reply]})
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text("❌ Xatolik yuz berdi.")

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("clear", clear))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
app.run_polling()
