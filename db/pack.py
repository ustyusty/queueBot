from .db import db
from datetime import date, timedelta
class PACK:
    def __init__(self):
        self.pool = db.pool

    async def get_pack_id_by_title(self, title: str, course_id: int):
        #вытаскивает id пака по его тайтлу
        async with self.pool.acquire() as conn:
            result = await conn.fetchval(
            """
            SELECT id
            FROM "pack"
            WHERE title = $1
            """,
            title)
        return result if result is not None else await self.add_pack(title, course_id)

    async def add_pack(self, title: str, course_id: int, deadline = date.today()+timedelta(days=7)):
        #добавляет пак
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO "pack" (title, courses_id, deadline)
                VALUES ($1, $2, $3)
                """,
            title,
            course_id,
            deadline
            )
    
    async def get_pack_id_by_course_id(self, course_id: int):
        #вытаскивает id пака по id курса
        async with self.pool.acquire() as conn:
            result = await conn.fetchval(
            """
            SELECT id
            FROM "pack"
            WHERE courses_id = $1
            """,
            course_id)
        return result if result is not None else await self.add_pack("Default Pack", course_id)