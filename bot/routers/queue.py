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

    async def get_active_entry(self, user_id: int, course_id: int) -> Record | None:
        return await self.db.fetchrow(
            """
            SELECT id, user_id, course_id, is_pass, register_at, close_at
            FROM list_queue
            WHERE user_id = $1
              AND course_id = $2
              AND is_pass = FALSE
              AND close_at IS NULL
            """,
            user_id,
            course_id,
        )

    async def join_queue(self, user_id: int, course_id: int) -> tuple[Record, bool]:
        current_entry = await self.get_active_entry(user_id, course_id)
        if current_entry is not None:
            return current_entry, False
        return await self.add_queue_entry(user_id, course_id), True

    async def finish_queue_entry(self, user_id: int, course_id: int) -> Record | None:
        return await self.db.fetchrow(
            """
            UPDATE list_queue
            SET is_pass = TRUE,
                close_at = CURRENT_TIMESTAMP
            WHERE user_id = $1
              AND course_id = $2
              AND is_pass = FALSE
              AND close_at IS NULL
            RETURNING id, user_id, course_id, is_pass, register_at, close_at
            """,
            user_id,
            course_id,
        )

    async def get_queue_position(self, entry_id: int) -> int:
        position = await self.db.fetchval(
            """
            SELECT COUNT(*)
            FROM list_queue AS other_queue
            JOIN "user" AS other_user ON other_user.id = other_queue.user_id
            JOIN list_queue AS selected_queue ON selected_queue.id = $1
            JOIN "user" AS selected_user ON selected_user.id = selected_queue.user_id
            WHERE other_queue.course_id = selected_queue.course_id
              AND other_user.group_id = selected_user.group_id
              AND other_queue.is_pass = FALSE
              AND other_queue.close_at IS NULL
              AND (
                  other_queue.register_at < selected_queue.register_at
                  OR (
                      other_queue.register_at = selected_queue.register_at
                      AND other_queue.id <= selected_queue.id
                  )
              )
            """,
            entry_id,
        )
        return int(position)

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
              AND (
                  NOT $3::BOOLEAN
                  OR (queue.is_pass = FALSE AND queue.close_at IS NULL)
              )
            ORDER BY queue.register_at, queue.id
            """,
            course_id,
            group_id,
            only_active,
        )
