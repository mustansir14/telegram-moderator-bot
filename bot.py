from telegram import Update, Bot
from telegram.ext import Updater, MessageHandler, filters, CallbackContext, ApplicationBuilder, ContextTypes

from dotenv import load_dotenv
import os

from negative_sentiment_analyzer import NegativeSentimentAnalyzer

load_dotenv()


analyzer = NegativeSentimentAnalyzer(os.getenv("OPENAI_API_KEY"))


async def delete_negative_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text
    chat_id = update.message.chat_id

    if analyzer.is_negative(message_text):
        await context.bot.delete_message(chat_id, update.message.message_id)


def main():

    app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    app.add_handler(MessageHandler(filters.TEXT & ~
                                   filters.COMMAND, delete_negative_messages))

    app.run_polling()


if __name__ == '__main__':
    main()
