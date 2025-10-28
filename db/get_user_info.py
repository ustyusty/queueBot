from .db import db
class USERINFO:
    def __init__(self):
        self.pool = db.pool

    async def get_user_id(self, tg_id):
        #вытаскивает id юзера по его тг
        async with self.pool.acquire() as conn:
            return await conn.fetchval(
            """
            SELECT id
            FROM "user"
            WHERE tg_id = $1
            """,
            tg_id)
    
    async def get_user_info(self, user_id):
        # вытаскивает всю инфу из таблицы по id
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(
            """
            SELECT *
            FROM "user"
            WHERE id = $1
            """,
            user_id)

    async def GUI(self, tg_id):
        user_id = await self.get_user_id(tg_id)
        return await self.get_user_info(user_id)
    
    async def user_exists(self, tg_id: int) -> bool:
        async with self.pool.acquire() as connection:
            result = await connection.fetchrow(
                """SELECT 1 FROM "user" WHERE tg_id = $1""", tg_id
            )
            return result is not None
    
    