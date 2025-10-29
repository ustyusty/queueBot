from .group import GROUP
class ADDUSER:
    def __init__(self, db):
        self.db = db
        self.pool = db.pool

    async def register_user(self, user, first_name, last_name, usergroup="47"):
        """
        Добавляет пользователя вместе с Telegram и группой.
        Если уже есть, обновляет данные.
        """
        group_id = await GROUP(self.db).get_group(usergroup)

        async with self.pool.acquire() as conn:
            async with conn.transaction():


                await conn.execute(
                    """
                    INSERT INTO "user" (tg_id, group_id, firstname, surname, username)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (tg_id)
                    DO UPDATE SET
                        group_id = EXCLUDED.group_id,
                        firstname = EXCLUDED.firstname,
                        surname = EXCLUDED.surname,
                        username = EXCLUDED.username;
                    """,
                    user.id,
                    group_id,
                    first_name,
                    last_name,
                    user.username
                )
    