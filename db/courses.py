class COURSES:
    def __init__(self, db):
        self.pool = db.pool

    async def get_course_id_by_title(self, title: str):
        #вытаскивает id курса по его тайтлу
        async with self.pool.acquire() as conn:
            result = await conn.fetchval(
            """
            SELECT id
            FROM "courses"
            WHERE title = $1
            """,
            title)
        return result if result is not None else await self.add_courses(title)

    async def add_courses(self, title: str):
        #добавляет курс и возвращает его id
        async with self.pool.acquire() as conn:
            course_id = await conn.fetchval(
                """
                INSERT INTO "courses" (title)
                VALUES ($1)
                RETURNING id
                """,
            title)
        return course_id

    async def get_courses_id_by_pack(self, pack_id: int):
        #вытаскивает id курса по id пака
        async with self.pool.acquire() as conn:
            return await conn.fetchval(
            """
            SELECT courses_id
            FROM "pack"
            WHERE id = $1
            """,
            pack_id)
    