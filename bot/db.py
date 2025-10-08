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

    async def update_user(self, user, first_name, last_name): # апдейт для пользователя
        async with self.pool.acquire() as conn:
            await conn.execute(
                """UPDATE users
                SET first_name = $2, last_name = $3
                WHERE user_id =$1
                """,
                user.id,
                first_name,
                last_name

            )
    async def set_done_is_pass(self, user):
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
            UPDATE list_queue 
            SET is_pass = TRUE
            WHERE user_id = $1
            """,
                user.id
            )

    async def put_on_queue(self, user):

        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO list_queue (user_id)
                SELECT $1
                WHERE NOT EXISTS (
                    SELECT 1 FROM list_queue WHERE user_id = $1
                )
                """,
                user.id
            )

    async def get_queue(self):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM list_queue
                ORDER BY created_at ASC
            """)
            return rows

    async def leave_queue(self, user):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                DELETE FROM list_queue
                WHERE user_id = $1;
            """,
            user.id
            )
            return rows
        
    async def get_user_info(self, user_id):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT username, first_name, last_name 
                FROM users 
                WHERE user_id = $1
            """, user_id)
            return dict(row) if row else {}
        
    async def cleanup_job(self):
        async with self.pool.acquire() as conn:
            await conn.execute("DELETE FROM list_queue WHERE created_at < NOW() AND is_pass = TRUE;")
        

db = DataBase()