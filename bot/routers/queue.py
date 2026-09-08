from asyncpg import Record

from database import DataBase


class QueueRepo:
    """Database operations for queue entries."""

    def __init__(self, db: DataBase):
        self.db = db

    async def add_queue_entry(self, user_id: int, course_id: int) -> Record:
        entry = await self.db.fetchrow(
            """
            INSERT INTO list_queue (user_id, course_id)
            VALUES ($1, $2)
            RETURNING id, user_id, course_id, is_pass, register_at, close_at
            """,
            user_id,
            course_id,
        )
        if entry is None:
            raise RuntimeError("Queue entry was not created")
        return entry

    async def get_queue_entry(self, entry_id: int) -> Record | None:
        return await self.db.fetchrow(
            """
            SELECT
                queue.id,
                queue.user_id,
                queue.course_id,
                users.group_id,
                queue.is_pass,
                queue.register_at,
                queue.close_at,
                users.tg_id,
                users.nicname,
                users.username,
                courses.title AS course_title,
                groups.title AS group_title
            FROM list_queue AS queue
            JOIN "user" AS users ON users.id = queue.user_id
            JOIN courses ON courses.id = queue.course_id
            LEFT JOIN groups ON groups.id = users.group_id
            WHERE queue.id = $1
            """,
            entry_id,
        )

    async def get_queue_entries(
        self,
        *,
        course_id: int | None = None,
        group_id: int | None = None,
        only_active: bool = False,
    ) -> list[Record]:
        return await self.db.fetchall(
            """
            SELECT
                queue.id,
                queue.user_id,
                queue.course_id,
                users.group_id,
                queue.is_pass,
                queue.register_at,
                queue.close_at,
                users.tg_id,
                users.nicname,
                users.username,
                courses.title AS course_title,
                groups.title AS group_title
            FROM list_queue AS queue
            JOIN "user" AS users ON users.id = queue.user_id
            JOIN courses ON courses.id = queue.course_id
            LEFT JOIN groups ON groups.id = users.group_id
            WHERE ($1::INTEGER IS NULL OR queue.course_id = $1)
              AND ($2::INTEGER IS NULL OR users.group_id = $2)
              AND (NOT $3::BOOLEAN OR queue.is_pass = FALSE)
            ORDER BY queue.register_at, queue.id
            """,
            course_id,
            group_id,
            only_active,
        )
