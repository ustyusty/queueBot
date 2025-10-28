from .db import db
from .courses import COURSES
from datetime import date
class PACK:
    def __init__(self):
        self.pool = db.pool

    async def get_pack(self, title: str):
        #вытаскивает id пака по его тайтлу
        async with self.pool.acquire() as conn:
            return await conn.fetchval(
            """
            SELECT id
            FROM "pack"
            WHERE title = $1
            """,
            title)

    async def add_pack(self, title: str, deadline: date, courses: str):
        #добавляет пак
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO "pack" (title, courses_id, deadline)
                VALUES ($1, $2, $3)
                """,
            title,
            await COURSES().get_courses_id(courses),
            deadline
            )
    