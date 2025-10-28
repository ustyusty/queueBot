import asyncpg
from dotenv import load_dotenv
import os

class DataBase:
    def __init__(self):
        load_dotenv()
        self.pool = None
    
    async def init(self):
        self.pool = await asyncpg.create_pool(
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            database=os.getenv("POSTGRES_DB"),
            host=os.getenv("POSTGRES_HOST"),
            port=int(os.getenv("POSTGRES_PORT", 5432)),
        )
        print("✅ Подключение к базе прошло успешно")

    async def close(self):
        if self.pool:
            await self.pool.close()
            print("🔒 Соединение с базой закрыто")

    

db = DataBase()