from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from bot.db import db

class InlineCallbackHandler:
    def __init__(self, app: Application):
        self.app = app
        self.db = db
        self.callback_map = {
            "put_on_queue": self._put_on_queue,
            "show_queue": self._show_queue,
            "leave_queue": self._leave_queue,
        }

        self.app.add_handler(CallbackQueryHandler(self.inline_callback))

    async def inline_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        print(f"⚡ Пришёл callback: {query.data}", flush=True)
        await query.answer()

        handler = self.callback_map.get(query.data)
        if handler:
            await handler(query)

    async def _put_on_queue(self, query):
        await self.db.put_on_queue(query.from_user)
        await query.edit_message_text("✅ Ты в очереди!")
    
    async def _show_queue(self, query):
        rows = await self.db.get_queue()

        if not rows:
            await query.edit_message_text("📭 Очередь пуста")
            return
        
        messages = []
        for i, r in enumerate(rows, 1):
            user_info = await self.db.get_user_info(r['user_id'])
            name = user_info.get('first_name') or user_info.get('username') or f"User {r['user_id']}"
            status = "✅" if r.get('is_pass') else "⏳"
            messages.append(f"{i}. {status} {name}")
    
        queue_text = "📋 Очередь:\n" + "\n".join(messages)
        await query.edit_message_text(queue_text)
    
    async def _leave_queue(self, query):
        await self.db.leave_queue(query.from_user)
        await query.edit_message_text("👋 Вышел из очереди")