from .db import db
from .group import GROUP
class ADDUSER:
    def __init__(self, user):
        self.user = user
        self.pool = db.pool
        self.user_id = user.id
        self.username = user.username
        self.firstname = user.firstname
        self.surname = user.lastname


    async def register_user(self):
        """
        Добавляет пользователя вместе с Telegram и группой.
        Если уже есть, обновляет данные.
        """
        group_id = await GROUP().get_group(self.user.group)

        async with self.pool.acquire() as conn:
            async with conn.transaction():


                await conn.execute(
                    """
                    INSERT INTO "user" (tg_id, group_id, firstname, surname)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (tg_id)
                    DO UPDATE SET
                        group_id = EXCLUDED.group_id,
                        firstname = EXCLUDED.firstname,
                        surname = EXCLUDED.surname;
                    """,
                    self.user_id,
                    group_id,
                    self.firstname,
                    self.surname
                )