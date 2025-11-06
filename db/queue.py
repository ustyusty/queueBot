class QUEUE:
    def __init__(self, db):
        self.pool = db.pool

    async def put_on_queue(self, user_id, course_id):
        # добавляет пользователя в очередь
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    """
                    INSERT INTO "list_queue"
                    (user_id, course_id)
                    VALUES ($1, $2)
                    ON CONFLICT ON CONSTRAINT unique_user_course DO NOTHING
                    """,
                    user_id,
                    course_id,
                )
        print(f"User {user_id} has been added to the queue for course {course_id}")

    async def get_queue(self, course_id):
        # вытаскивает всю инфу из таблицы list_queue, связанной с курсом
        
        async with self.pool.acquire() as conn:
            return await conn.fetch(
            """
            SELECT *
            FROM "list_queue"
            WHERE course_id = $1
            """,
            course_id)

    async def set_is_pass(self, user_id, course_id):
        # устанавливает is_pass в True для пользователя в очереди
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE "list_queue"
                SET is_pass = TRUE
                WHERE user_id = $1 AND course_id = $2
                """,
                user_id,
                course_id
            )
        print(f"User {user_id} has passed course {course_id}")

    async def leave_queue(self, user_id: int, course_id: int):
        # удаляет пользователя из очереди
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                DELETE FROM "list_queue"
                WHERE user_id = $1 AND course_id = $2
                """,
                user_id,
                course_id
            )
        print(f"User {user_id} has left the queue")

    async def cleanup_job(self, course_id: int):
        async with self.pool.acquire() as conn:
            await conn.execute(
                """DELETE FROM "list_queue"
                 WHERE put_time < NOW() AND course_id = $1
                """,
                course_id
            )
    async def get_queue_id(self, user_id: int, course_id: int):
        # вытаскивает id из таблицы list_queue для пользователя и курса
        async with self.pool.acquire() as conn:
            result = await conn.fetchrow(
                """
                SELECT id
                FROM "list_queue"
                WHERE user_id = $1 AND course_id = $2
                """,
                user_id,
                course_id
            )
        return result['id'] if result else None