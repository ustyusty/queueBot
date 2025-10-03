from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from bot.db import db

class StartHandler:
    def __init__(self, app: Application):
        self.app = app
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("menu", self.menu))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        await db.save_user(user)
        await self.menu(update, context)

    async def menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("встать в очередь", callback_data="put_on_queue")],
             [InlineKeyboardButton("показать очередь", callback_data="show_queue")],
             [InlineKeyboardButton("выйти из очереди", callback_data="leave_queue")]]
        )
        await update.message.reply_text(
            f"Привет, {user.first_name}! 👋 Вот что я могу для тебя сделать:",
            reply_markup=keyboard
        )
