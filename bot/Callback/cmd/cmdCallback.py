from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from bot.keyboards.inline import MainMenuKeyboard, CommonKeyboard
from db.db import db
from db.get_user_info import USERINFO
from db.queue import QUEUE
from db.courses import COURSES
from bot.massages import main_menu


class CommandCallbackHandler:
    
    def __init__(self, app: Application):
        self.app = app
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("menu", self.menu))
        self.app.add_handler(CommandHandler("clear_queue", self.clear_queue))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user

        if not await USERINFO(db).user_exists(user.id):
            await update.message.reply_text(
                f"👋 Привет, {user.first_name}! "
                "Добро пожаловать в наш бот.\n Пожалуйста, /register."
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
    async def clear_queue(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        course_title = context.user_data["step"]  # Extract course title from callback data
        course_id = await COURSES(db).get_course_id_by_title(course_title)  #
        if user.id in [1007912517]:  # Replace with actual admin user IDs
            await QUEUE(db).cleanup_job(course_id)
            await update.message.reply_text(
                f"Оередь очищена"
            )
            await self.menu(update, context)
