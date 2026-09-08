import logging
from database import DataBase
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from routers import UserRepo
from time import sleep

def get_dsn() -> str:
    from core import (
            DB_HOST, 
            DB_NAME, 
            DB_PASSWORD, 
            DB_PORT, 
            DB_USER
            )
    dsn = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return dsn

class BotApp: 
    def __init__(self, token: str):
        self.application = Application.builder().token(token).post_init(self.post_init).build()

    async def post_init(self, app: Application):
        db = DataBase(dsn=get_dsn()) 
        db.connect()
        sleep(1)
        app.bot_data['UserRouter'] = UserRepo(db)

    def run(self):
        self.application.run_polling()


if __name__ == "__main__":
    from core import BOT_TOKEN
    BotApp(token=BOT_TOKEN).run()
