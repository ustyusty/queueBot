from datetime import date, timedelta
class PACK:
    def __init__(self, db):
        self.pool = db.pool

    async def get_pack_id_by_title(self, title: str):
        #вытаскивает id пака по его тайтлу
        async with self.pool.acquire() as conn:
            result = await conn.fetchval(
            """
            SELECT id
            FROM "pack"
            WHERE title = $1
            """,
            title)
        return result

    async def add_pack(self, title: str, course_id: int, deadline = date.today()+timedelta(days=7)):
        #добавляет пак
        async with self.pool.acquire() as conn:
            return await conn.fetchval(
                """
                INSERT INTO "pack" (title, courses_id, deadline)
                VALUES ($1, $2, $3)
                RETURNING id
                """,
            title,
            course_id,
            deadline
            )