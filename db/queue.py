from .db import db
class QUEUE:
    def __init__(self):
        self.pool = db.pool

    async def put_on_queue(self, user_id, pack_id, priority):
        # добавляет пользователя в очередь
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    """
                    INSERT INTO "list_queue"
                    (user_id, pack_id, priority_queue)
                    VALUES ($1, $2, $3)
                    """,
                    user_id,
                    pack_id,
                    priority
                )

    async def get_queue(self):
        # вытаскивает всю инфу из таблицы list_queue
        async with self.pool.acquire() as conn:
            return await conn.fetch(
            """
            SELECT *
            FROM "list_queue"
            """)
