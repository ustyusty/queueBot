class QUEUE:
    def __init__(self, db):
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
                    ON CONFLICT (user_id, pack_id) DO NOTHING
                    """,
                    user_id,
                    pack_id,
                    priority
                )
        print(f"User {user_id} has been added to the queue for pack {pack_id}")

    async def get_queue(self, course_id):
        # вытаскивает всю инфу из таблицы list_queue, связанной с курсом
        
        async with self.pool.acquire() as conn:
            return await conn.fetch(
            """
            SELECT *
            FROM "list_queue" as lq
            JOIN "pack" p ON lq.pack_id = p.id
            WHERE p.courses_id = $1
            """,
            course_id)

    async def set_is_pass(self, user_id, pack_id):
        # устанавливает is_pass в True для пользователя в очереди
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE "list_queue"
                SET is_pass = TRUE
                WHERE user_id = $1 AND pack_id = $2
                """,
                user_id,
                pack_id
            )
        print(f"User {user_id} has passed pack {pack_id}")

    async def leave_queue(self, user_id: int, pack_id: int):
        # удаляет пользователя из очереди
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                DELETE FROM "list_queue"
                WHERE user_id = $1 AND pack_id = $2
                """,
                user_id,
                pack_id
            )
        print(f"User {user_id} has left the queue for pack {pack_id}")

    async def cleanup_job(self, course_id: int):
        async with self.pool.acquire() as conn:
            await conn.execute(
                """DELETE FROM "list_queue" lq
                JOIN "pack" p ON lq.pack_id = p.id
                 WHERE lq.created_at < NOW() AND p.courses_id = $1
                """,
                course_id
            )
