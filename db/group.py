from .db import db
class GROUP:
    def __init__(self):
        self.pool = db.pool

    async def get_group(self, title: str):
        #вытаскивает id группы по его тайтлу
        async with self.pool.acquire() as conn:
            return await conn.fetchval(
            """
            SELECT id
            FROM "group"
            WHERE title = $1
            """,
            title)

    async def add_group(self, title: str):
        #добавляет групппу
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO "group" (title)
                VALUES ($1)
                ON CONFLICT (title) DO NOTHING
                """,
            title)
    