from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from .command import inlineCommand
from bot.keyboards.inline import MainMenuKeyboard
from bot.db import db

class InlineCallbackHandler:
    def __init__(self, app: Application):
        self.app = app
        self.db = db
        command = inlineCommand(self.db)
        self.callback_map = {
            "put_on_queue": command.put_on_queue,
            "show_queue": command.show_queue,
            "leave_queue": command.leave_queue,
            "back_to_menu": self._back_to_menu,
        }

        self.app.add_handler(CallbackQueryHandler(self.inline_callback))

    async def inline_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        print(f"⚡ Пришёл callback: {query.data}", flush=True)
        await query.answer()

        handler = self.callback_map.get(query.data)
        if handler:
            await handler(query)

    async def _back_to_menu(self, query):
        await query.edit_message_text(
            """« Главное меню »
                ✨ · ✦ · ✨
                📅 Очередь сбрасывается:
                вторник и четверг | после 16:00
                
                🐞 Баги и предложения:
                ⬤ в лс @UstyUsty
                ✨ · ✦ · ✨""",
            reply_markup = MainMenuKeyboard.inline()
        )