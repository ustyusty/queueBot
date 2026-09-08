import logging

from database import DataBase
from telegram import User

logger = logging.getLogger(__name__)


class UserRepo:
    def __init__(self, db: DataBase):
        self.db = db

    async def register_user(self, user: User) -> int:
        return await self.db.fetchval(
            """
            INSERT INTO "user" (tg_id, nicname, username)
            VALUES ($1, $2, $3)
            ON CONFLICT (tg_id) DO UPDATE SET
                nicname = EXCLUDED.nicname,
                username = EXCLUDED.username
            RETURNING id
            """,
            user.id,
            user.first_name,
            user.username,
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
