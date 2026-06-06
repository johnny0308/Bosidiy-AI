import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import google.genai as genai

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ["TELEGRAM_TOKEN"]
GEMINI_KEY = os.environ["GEMINI_KEY"]

client = genai.Client(api_key=GEMINI_KEY)
histories = {}

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Salom! Men AI botman.\n"
        "Savolingizni yozing!\n"
        "/clear — suhbatni tozalash"
    )

async def clear(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    histories[update.effective_user.id] = []
    await update.message.reply_text("✅ Tozalandi!")

async def reply(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text
    histories.setdefault(uid, [])
    await ctx.bot.send_chat_action(update.effective_chat.id, "typing")
    try:
        histories[uid].append({"role": "user", "parts": [{"text": text}]})
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=histories[uid]
        )
        answer = response.text
        histories[uid].append({"role": "model", "parts": [{"text": answer}]})
        if len(histories[uid]) > 20:
            histories[uid] = histories[uid][-20:]
        await update.message.reply_text(answer)
    except Exception as e:
        logging.error(e)
        await update.message.reply_text("❌ Xatolik yuz berdi.")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("clear", clear))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
app.run_polling()
