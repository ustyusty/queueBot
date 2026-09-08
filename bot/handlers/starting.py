from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

from routers import UserRepo

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    repo:UserRepo = context.bot_data.get("UserRepo")
    await update.message.reply_text(
            f"👋 Привет, {user.first_name}!") 
    repo.register_user(user)