from database import DataBase
from telegram import User

class UserRepo:
    def __init__(self, db:DataBase):
        self.db = db
            
    async def register_user(self, user:User):
        await self.db.execute(
            """
            INSERT INTO "user" (tg_id, nicname, username)
            VALUES ($1, $2, $3)
            RETURNING id
            """,
            user.id,
            user.first_name,
            user.username
        )