from negative_sentiment_analyzer import NegativeSentimentAnalyzer
from telegram import Update
from telegram.ext import MessageHandler, filters, ApplicationBuilder, ContextTypes

from dotenv import load_dotenv
import os
import logging
logging.basicConfig(format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)


load_dotenv()


analyzer = NegativeSentimentAnalyzer(os.getenv("OPENAI_API_KEY"))

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PORT = int(os.environ.get("PORT", 13978))
DISABLE_THREADS = [-1001622898322]

chat_admins = {}


async def delete_negative_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = update.message
    if message is None:
        message = update.edited_message
    message_text = message.text
    chat_id = message.chat_id
    user_id = message.from_user.id
    thread_id = message.message_thread_id

    logging.info(f"Message {message_text} in thread {thread_id}")

    if chat_id in DISABLE_THREADS:
        return

    if chat_id not in chat_admins:
        try:
            admins = await context.bot.get_chat_administrators(chat_id)
            chat_admins[chat_id] = [admin.user.id for admin in admins]
        except:
            chat_admins[chat_id] = []

    if user_id in chat_admins[chat_id]:
        return

    if analyzer.is_negative(message_text):
        logging.info(f"Deleting negative message \"{message_text}\"")
        await context.bot.delete_message(chat_id, message.message_id)


def main():

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~
                                   filters.COMMAND, delete_negative_messages))

    # app.run_polling()

    app.run_webhook(
        "0.0.0.0", PORT, TELEGRAM_BOT_TOKEN, webhook_url="https://telegram-moderator-bot-ace7cd090436.herokuapp.com/" + TELEGRAM_BOT_TOKEN)


if __name__ == '__main__':
    main()
