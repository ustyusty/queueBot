from telegram import Update
from telegram.ext import ContextTypes

class MainHandler:
    def __init__(self):
        self.callback_map = {}

    def register_callback(self, action, fn):
        self.callback_map[action] = fn

    async def inline_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        action_name, separator, action_param = query.data.partition(':')
        action_param = action_param if separator else None
        
        print(f"🔍 CALLBACK: '{query.data}' -> action='{action_name}', params={action_param}")
        if action_name in self.callback_map:
            handler = self.callback_map[action_name]
            return await handler(query, int(action_param)) if action_param else await handler(query)

main_handler = MainHandler()