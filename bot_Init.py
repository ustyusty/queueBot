from telegram.ext import Application
from bot.Callback.inline.inlineCallback import InlineCallbackHandler
from bot.Callback.cmd.cmdCallback import CommandCallbackHandler
from bot.Callback.cmd.regCallback import RegistrationHandler
from bot.db import db
from bot.scheduler import cleanup_scheduler
import asyncio
class BotApp:
    def __init__(self, token: str):
        self.application = Application.builder().token(token).post_init(self.post_init).build()
        self.register_handlers()
        print("🤖 Бот запущен...")

    async def post_init(self, app):
        await db.init()
        print("✅ База данных подключена.")
        asyncio.create_task(cleanup_scheduler())

    def register_handlers(self):
        self._handlers = [
            CommandCallbackHandler(self.application),
            InlineCallbackHandler(self.application),
            RegistrationHandler(self.application),
        ]

    def run(self):
        self.application.run_polling()