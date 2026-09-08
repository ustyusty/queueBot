import os 
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
DB_USER=os.getenv("DB_USER", "postgres")
DB_PASSWORD=os.getenv("DB_PASSWORD")
DB_NAME=os.getenv("DB_NAME", "postgres")
DB_HOST=os.getenv("DB_HOST", "127.0.0.1")
DB_PORT=os.getenv("DB_PORT", "5432")

