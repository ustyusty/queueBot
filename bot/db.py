import asyncpg
import asyncio
import os
from dotenv import load_dotenv

class DataBase:
    def __init__(self):
        load_dotenv()
        self.pool = None

    async def init(self, retries=10, delay=2):
        for i in range(retries):
            try:
                self.pool = await asyncpg.create_pool(
                    user=os.getenv("POSTGRES_USER"),
                    password=os.getenv("POSTGRES_PASSWORD"),
                    database=os.getenv("POSTGRES_DB"),
                    host=os.getenv("POSTGRES_HOST", "db"),
                    port=int(os.getenv("POSTGRES_PORT", 5432)),
                )
                print("✅ Подключение к базе прошло успешно")
                return
            except Exception as e:
                print(f"Попытка {i+1} не удалась: {e}")
                await asyncio.sleep(delay)
        raise Exception("Не удалось подключиться к базе")


    async def save_user(self, user):
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO users (user_id, username, first_name, last_name)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (user_id) DO NOTHING;
                """,
                user.id,
                user.username,
                user.first_name,
                user.last_name
            )

    async def put_on_queue(self, update):
        text = update.message.text
        user_id = update.message.from_user.id

        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO messages (user_id, text)
                VALUES ($1, $2)
                """,
                user_id,
                text
            )

    async def get_queue(self, user):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM reminders
            """)
            return rows

db = DataBase()