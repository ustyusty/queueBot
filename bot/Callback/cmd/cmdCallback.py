from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from bot.keyboards.inline import MainMenuKeyboard, CommonKeyboard
from bot.db import db
from bot.massages import main_menu


class CommandCallbackHandler:
    
    def __init__(self, app: Application):
        self.app = app
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("menu", self.menu))
        self.app.add_handler(CommandHandler("clear_queue", self._clear_queue))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        await db.save_user(user)
        await self.menu(update, context)

    async def menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        keyboard = MainMenuKeyboard.inline()
        await update.message.reply_text(
            main_menu.text,
            reply_markup=keyboard
        )

    async def _clear_queue(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if user.id == 1007912517:
            await db.cleanup_job()
            keyboard = CommonKeyboard.back_to_main()
            await update.message.reply_text("бд очищена",reply_markup=keyboard)