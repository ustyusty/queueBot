import logging

from asyncpg import Record
from database import DataBase
from telegram import User

logger = logging.getLogger(__name__)


class UserRepo:
    def __init__(self, db: DataBase):
        self.db = db

    async def get_user(self, telegram_id: int = None, username: str = None) -> Record | None:
        if telegram_id is None and username is None:
            raise ValueError("Either telegram_id or username must be provided")
        argument = ["tg_id" if telegram_id is not None else "username", 
                    telegram_id if telegram_id is not None else username]
        return await self.db.fetchrow(
            f"""
            SELECT id, tg_id, group_id, nicname, username, is_admin, register_at
            FROM "user"
            WHERE {argument[0]} = $1
            """,
            argument[1]
        )

    async def register_user(
        self,
        user: User,
        nicname: str,
        group_id: int,
    ) -> int:
        return await self.db.fetchval(
            """
            INSERT INTO "user" (tg_id, nicname, username, group_id)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (tg_id) DO UPDATE SET
                nicname = EXCLUDED.nicname,
                username = EXCLUDED.username,
                group_id = EXCLUDED.group_id
            RETURNING id
            """,
            user.id,
            nicname,
            user.username,
            group_id,
        )

    async def change_group(self, telegram_id: int, group_id: int) -> Record | None:
        return await self.db.fetchrow(
            """
            UPDATE "user"
            SET group_id = $2
            WHERE tg_id = $1
            RETURNING id, tg_id, group_id, nicname, username, is_admin, register_at
            """,
            telegram_id,
            group_id,
        )

    async def is_admin(self, telegram_id: int) -> bool:
        result = await self.db.fetchval(
            """
            SELECT is_admin
            FROM "user"
            WHERE tg_id = $1
            """,
            telegram_id,
        )
        return bool(result)

    async def set_admin(self, telegram_id: int, is_admin: bool = True) -> bool:
        user_id = await self.db.fetchval(
            """
            UPDATE "user"
            SET is_admin = $2
            WHERE tg_id = $1
            RETURNING id
            """,
            telegram_id,
            is_admin,
        )
        updated = user_id is not None
        if updated:
            logger.info(
                "User admin status changed: tg_id=%s is_admin=%s",
                telegram_id,
                is_admin,
            )
        else:
            logger.warning("Cannot change admin status: tg_id=%s not found", telegram_id)
        return updated
