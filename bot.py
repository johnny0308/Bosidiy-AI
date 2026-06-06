import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ["TELEGRAM_TOKEN"]
GEMINI_KEY = os.environ["GEMINI_KEY"]

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"

histories = {}

def ask_gemini(messages):
    contents = []
    for m in messages:
        contents.append({
            "role": m["role"],
            "parts": [{"text": m["text"]}]
        })
    resp = requests.post(GEMINI_URL, json={"contents": contents})
    data = resp.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Salom! Men Bosidiy AI botman!\n\n"
        "🤖 AI bilan suhbat — shunchaki yozing\n"
        "📩 Admin bilan bog'lanish — /contact\n"
        "/clear — suhbatni tozalash"
    )

async def clear(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    histories[update.effective_user.id] = []
    await update.message.reply_text("✅ Suhbat tozalandi!")

async def contact(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📩 Adminga xabar: /send [xabar]")

async def send_to_owner(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    owner_id = int(os.environ.get("OWNER_ID", "0"))
    if not ctx.args:
        await update.message.reply_text("❗ /send [xabar]")
        return
    user = update.effective_user
    text = " ".join(ctx.args)
    msg = f"📩 Yangi xabar!\n👤 {user.full_name}\n🆔 {user.id}\n@{user.username or 'yoq'}\n\n💬 {text}"
    await ctx.bot.send_message(chat_id=owner_id, text=msg)
    await update.message.reply_text("✅ Yuborildi!")

async def ai_reply(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text
    histories.setdefault(uid, [])
    await ctx.bot.send_chat_action(update.effective_chat.id, "typing")
    histories[uid].append({"role": "user", "text": text})
    if len(histories[uid]) > 20:
        histories[uid] = histories[uid][-20:]
    try:
        reply = ask_gemini(histories[uid])
        histories[uid].append({"role": "model", "text": reply})
        await update.message.reply_text(reply)
    except Exception as e:
        logging.error(e)
        await update.message.reply_text(f"❌ Xatolik: {str(e)[:200]}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("clear", clear))
app.add_handler(CommandHandler("contact", contact))
app.add_handler(CommandHandler("send", send_to_owner))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_reply))
app.run_polling()
