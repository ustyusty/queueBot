from .db import db
class COURSES:
    def __init__(self):
        self.pool = db.pool

    async def get_courses_id(self, title: str):
        #вытаскивает id курса по его тайтлу
        async with self.pool.acquire() as conn:
            return await conn.fetchval(
            """
            SELECT id
            FROM "courses"
            WHERE title = $1
            """,
            title)

    async def add_courses(self, title: str):
        #добавляет курс
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO "courses" (title)
                VALUES ($1)
                ON CONFLICT (title) DO NOTHING
                """,
            title)
    