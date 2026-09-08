from asyncpg import Record

from database import DataBase


class GroupRepo:
    """Database operations for student groups."""

    def __init__(self, db: DataBase):
        self.db = db

    async def add_group(self, title: str) -> Record:
        group = await self.db.fetchrow(
            """
            INSERT INTO groups (title)
            VALUES ($1)
            ON CONFLICT (title) DO UPDATE SET title = EXCLUDED.title
            RETURNING id, title
            """,
            title,
        )
        if group is None:
            raise RuntimeError("Group was not created")
        return group

    async def get_group(self, group_id: int) -> Record | None:
        return await self.db.fetchrow(
            """
            SELECT id, title
            FROM groups
            WHERE id = $1
            """,
            group_id,
        )

    async def get_groups(self) -> list[Record]:
        return await self.db.fetchall(
            """
            SELECT id, title
            FROM groups
            ORDER BY title, id
            """
        )
