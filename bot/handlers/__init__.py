from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from .starting import start


def register_handler(app: Application):
    app.add_handler(CommandHandler("start", start))