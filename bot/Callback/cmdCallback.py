from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from bot.db import db

class StartHandler:
    def __init__(self, app: Application):
        self.app = app
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("menu", self.menu))
        self.app.add_handler(CallbackQueryHandler(self.inline_callback))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        await db.save_user(user)
        await self.menu(update, context)

    async def menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("встать в очередь", callback_data="put_on_queue")],
             [InlineKeyboardButton("show очередь", callback_data="show_queue")]]
        )
        await update.message.reply_text(
            f"Привет, {user.first_name}! 👋 Вот что я могу для тебя сделать:",
            reply_markup=keyboard
        )

    async def inline_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        print(f"⚡ Пришёл callback: {query.data}", flush=True)
        await query.answer()

        if query.data == "put_on_queue":
            await db.put_on_queue(update.effective_user)
            await query.edit_message_text("✅ Ты в очереди!")
        
        elif query.data == "show_queue":
            rows = await db.get_queue()
            if rows:
                messages = "\n".join(f"{r['name']}" for r in rows)
                await query.edit_message_text(f"📋 Очередь:\n{messages}")
            else:
                await query.edit_message_text("Очередь пуста.")
        
