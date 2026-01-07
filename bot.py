from src.negative_sentiment_analyzer import NegativeSentimentAnalyzer
from telegram import Update
from telegram.ext import MessageHandler, filters, ApplicationBuilder, ContextTypes

from dotenv import load_dotenv
import os
import logging
logging.basicConfig(format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)


load_dotenv()

ENVIRON = os.getenv("ENVIRON")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"


analyzer = NegativeSentimentAnalyzer(os.getenv("OPENAI_API_KEY"))

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PORT = 3000
BAN_STICKER_SETS = [
    "Lustful",
    "IgnoranzaRegna",
    "vsrpron",
    "CryptoCurvepack",
    "Tresxxx",
    "sexNfun",
    "rbkp01",
    "johnnysinsbrazzers",
    "PornActress",
    "James_Deen_stickers",
    "BrotherhoodBald",
    "Sexting",
    "MyDick",
    "Genitalia_stickers",
    "GayRainbowStickers",
    "Cnaked",
    "Hottie",
    "Pooorno",
    "Porn87",
    "xxxpornxxx",
    "pornguys",
    "Pornstars1",
    "Thomascuck"
]


# format {chat_id : [thread_ids]}
# Single source of truth: determines which chats to moderate and where to send reminders
if ENVIRON == "prod":
    THREADS_TO_MODERATE = {
        -1001622898322: [158009, 110538, 238474, None]
    }
else:
    THREADS_TO_MODERATE = {
        -1001843081678: [213]
    }


chat_admins = {}


async def delete_negative_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = update.message
    if message is None:
        message = update.edited_message
    if message is None:
        return

    message_text = message.text
    if message_text is None:
        return

    chat_id = message.chat_id

    if message_text.startswith("/"):
        logging.info(f"Deleting command \"{message_text}\"")
        await context.bot.delete_message(chat_id, message.message_id)
        return

    user_id = message.from_user.id
    thread_id = message.message_thread_id

    # Only moderate chats defined in THREADS_TO_MODERATE
    if chat_id not in THREADS_TO_MODERATE:
        return
    if thread_id not in THREADS_TO_MODERATE[chat_id]:
        return

    logging.info(
        f"Message {message_text} with chat_id {chat_id} and thread_id {thread_id}")

    if chat_id not in chat_admins:
        try:
            admins = await context.bot.get_chat_administrators(chat_id)
            chat_admins[chat_id] = [admin.user.id for admin in admins]
        except:
            chat_admins[chat_id] = []

    # Skip admin moderation unless DEBUG is enabled
    if not DEBUG and user_id in chat_admins[chat_id]:
        return

    if analyzer.is_negative(message_text):
        logging.info(f"Deleting negative message \"{message_text}\"")
        await context.bot.delete_message(chat_id, message.message_id)


async def delete_negative_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if message is None:
        return

    chat_id = message.chat_id

    # Only moderate chats defined in THREADS_TO_MODERATE
    if chat_id not in THREADS_TO_MODERATE:
        return

    sticker = message.sticker
    if sticker and sticker.set_name in BAN_STICKER_SETS:
        await context.bot.delete_message(
            message.chat_id, message.message_id)


async def send_reminder_message(context: ContextTypes.DEFAULT_TYPE):
    text = "📢 Reminder:\n\nThis chat is only for trade-talk. For off-topic discussions, please head to the off-topic chat. Let's stay on point! 🎯 Thanks! ✌️"
    await context.bot.send_message(
        chat_id=context.job.data["chat_id"], message_thread_id=context.job.data["thread_id"], text=text)


def main():

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT, delete_negative_messages))

    app.add_handler(MessageHandler(
        filters.ATTACHMENT, delete_negative_sticker))

    j = app.job_queue
    for chat_id, thread_ids in THREADS_TO_MODERATE.items():
        seconds = get_value(0, 57600)
        for thread_id in thread_ids:
            interval = get_value(30, 86400)
            j.run_repeating(send_reminder_message, interval, seconds, data={
                            "chat_id": chat_id, "thread_id": thread_id})
            seconds += get_value(10, 600)

    # if ENVIRON == "prod":
    #     logging.info("Running webhook")
    #     app.run_webhook(
    #         "0.0.0.0", PORT, TELEGRAM_BOT_TOKEN, webhook_url="https://165.232.74.108/" + TELEGRAM_BOT_TOKEN)
    # else:
    logging.info("Running polling")
    app.run_polling()


def get_value(dev_value, prod_value):
    if ENVIRON == "prod":
        return prod_value
    else:
        return dev_value


if __name__ == '__main__':
    main()
