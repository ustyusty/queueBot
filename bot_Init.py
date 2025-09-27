from telegram.ext import Application
from bot.Callback.inlineCallback import InlineCallbackHandler
from bot.Callback.cmdCallback import StartHandler
from bot.db import db


class BotApp:
    def __init__(self, token: str):
        self.application = Application.builder().token(token).post_init(self.post_init).build()
        self.register_handlers()
        print("🤖 Бот запущен...")




    async def post_init(self, app):
        await db.init()
        print("✅ База данных подключена.")

    def register_handlers(self):
        StartHandler(self.application)


    def run(self):
        self.application.run_polling()