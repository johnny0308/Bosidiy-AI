import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ["TELEGRAM_TOKEN"]
GEMINI_KEY = os.environ["GEMINI_KEY"]
OWNER_ID = int(os.environ["OWNER_ID"])  # Sizning Telegram ID

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-1.5-flash-latest")
histories = {}

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Salom! Men Bosidiy AI botman!\n\n"
        "🤖 AI bilan suhbat — shunchaki yozing\n"
        "📩 Admin bilan bog'lanish — /contact"
    )

async def clear(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    histories[update.effective_user.id] = []
    await update.message.reply_text("✅ Suhbat tozalandi!")

async def contact(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📩 Adminga xabar yuboring:\n"
        "Xabaringizni yozing, /send dan keyin:"
        "\nMasalan: /send Salom, savol bor edi"
    )

async def send_to_owner(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("❗ Xabar yozing: /send [xabar]")
        return
    user = update.effective_user
    text = " ".join(ctx.args)
    msg = (
        f"📩 Yangi xabar!\n"
        f"👤 Ismi: {user.full_name}\n"
        f"🆔 ID: {user.id}\n"
        f"📱 Username: @{user.username or 'yoq'}\n\n"
        f"💬 Xabar: {text}"
    )
    await ctx.bot.send_message(chat_id=OWNER_ID, text=msg)
    await update.message.reply_text("✅ Xabaringiz adminga yuborildi!")

async def reply_to_user(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    # Admin javob berish: /reply [user_id] [xabar]
    if update.effective_user.id != OWNER_ID:
        return
    if len(ctx.args) < 2:
        await update.message.reply_text("❗ Format: /reply [user_id] [xabar]")
        return
    user_id = int(ctx.args[0])
    text = " ".join(ctx.args[1:])
    await ctx.bot.send_message(chat_id=user_id, text=f"📬 Admin javobi:\n{text}")
    await update.message.reply_text("✅ Javob yuborildi!")

async def ai_reply(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text
    histories.setdefault(uid, [])
    await ctx.bot.send_chat_action(update.effective_chat.id, "typing")
    try:
        chat = model.start_chat(history=histories[uid])
        res = chat.send_message(text)
        histories[uid] = chat.history[-20:]
        await update.message.reply_text(res.text)
    except Exception as e:
        logging.error(e)
        await update.message.reply_text(f"❌ Xatolik: {str(e)}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("clear", clear))
app.add_handler(CommandHandler("contact", contact))
app.add_handler(CommandHandler("send", send_to_owner))
app.add_handler(CommandHandler("reply", reply_to_user))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_reply))
app.run_polling()
