from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from .command import inlineCommand
from bot.keyboards.inline import MainMenuKeyboard
from db.db import db
from bot.massages import main_menu

class InlineCallbackHandler:
    def __init__(self, app: Application):
        self.app = app
        if db.pool: print("pool lives into callback")
        command = inlineCommand(db)

        self.callback_map = {"back_to_menu": self._back_to_menu}
        
        courses_titles = ['A', 'B', 'C']  
        for queue_title in courses_titles:
            self.callback_map.update({
                f"put_on_queue_{queue_title}": command.put_on_queue,
                f"show_queue_{queue_title}": command.show_queue,
                f"leave_queue_{queue_title}": command.leave_queue,
                f"done_{queue_title}": command.set_done,
            })
        
        self.app.add_handler(CallbackQueryHandler(self.inline_callback))

    async def inline_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        if query.data.split('_')[0] =="show":
            context.user_data["step"] = query.data.split('_')[-1] 
        print(context.user_data)
        print(f"⚡ Пришёл callback: {query.data}", flush=True)
        await query.answer()

        handler = self.callback_map.get(query.data)
        if handler:
            await handler(query, context)

    async def _back_to_menu(self, query, context):
        await query.edit_message_text(main_menu.text, reply_markup=MainMenuKeyboard.inline())