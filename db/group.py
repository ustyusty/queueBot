
class GROUP:
    def __init__(self, db):
        self.pool = db.pool

    async def get_group(self, title: str):
        #вытаскивает id группы по его тайтлу
        async with self.pool.acquire() as conn:
            result = await conn.fetchval(
            """
            SELECT id
            FROM "group"
            WHERE title = $1
            """,
            title)

        return result if result is not None else await self.add_group(title)

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
    
    
