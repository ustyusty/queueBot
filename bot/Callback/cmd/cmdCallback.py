from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from bot.keyboards.inline import MainMenuKeyboard, CommonKeyboard
from db.db import db
from db.get_user_info import USERINFO
from bot.massages import main_menu


class CommandCallbackHandler:
    
    def __init__(self, app: Application):
        self.app = app
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("menu", self.menu))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user

        if not await USERINFO().user_exists(user.id):
            await update.message.reply_text(
                f"👋 Привет, {user.first_name}! "
                "Добро пожаловать в наш бот.\n Пожалуйста, зарегистрируйтесь, используя команду /register."
            )
        else:
            await update.message.reply_text(
                f"👋 С возвращением, {user.first_name}!"
            )
            await self.menu(update, context)

    async def menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        keyboard = MainMenuKeyboard.inline()
        await update.message.reply_text(
            main_menu.text,
            reply_markup=keyboard
        )