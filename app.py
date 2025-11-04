from dotenv import load_dotenv
import os
import logging
from bot_Init import BotApp

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
import tracemalloc
tracemalloc.start()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)



if __name__ == "__main__":
    BotApp(token=BOT_TOKEN).run()