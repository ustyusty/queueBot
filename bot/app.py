import logging

from database import DataBase
from telegram.ext import Application, ContextTypes

from bot.handlers import register_handler
from bot.routers import CourseRepo, GroupRepo, QueueRepo, UserRepo
from core.loger import setup_logging

logger = logging.getLogger(__name__)

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
        setup_logging()
        self.application = (
            Application.builder()
            .token(token)
            .post_init(self.post_init)
            .post_shutdown(self.post_shutdown)
            .build()
        )
        register_handler(self.application)
        self.application.add_error_handler(self.on_error)
        logger.info("Telegram handlers registered")

    async def post_init(self, app: Application):
        logger.info("Starting bot initialization")
        db = DataBase(dsn=get_dsn()) 
        await db.connect()
        app.bot_data['db'] = db
        app.bot_data['UserRouter'] = UserRepo(db)
        app.bot_data['CourseRepo'] = CourseRepo(db)
        app.bot_data['GroupRepo'] = GroupRepo(db)
        app.bot_data['QueueRepo'] = QueueRepo(db)
        logger.info("Bot initialization completed")

    async def post_shutdown(self, app: Application):
        logger.info("Stopping bot")
        db: DataBase | None = app.bot_data.get('db')
        if db is not None:
            await db.close()
        logger.info("Bot stopped")

    async def on_error(
        self,
        update: object,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        error = context.error
        if error is None:
            logger.error("Unknown error while processing Telegram update")
            return
        logger.error(
            "Unhandled error while processing Telegram update",
            exc_info=(type(error), error, error.__traceback__),
        )

    def run(self):
        logger.info("Starting Telegram polling")
        self.application.run_polling()


if __name__ == "__main__":
    from core import BOT_TOKEN
    BotApp(token=BOT_TOKEN).run()
