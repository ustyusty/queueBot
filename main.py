from db.add_user import ADDUSER
from db.get_user_info import USERINFO
from db.courses import COURSES
from db.pack import PACK
from db.queue import QUEUE
from db.group import GROUP
import asyncio
from datetime import date
import asyncpg
from dotenv import load_dotenv
import os
import time
class DataBase:
    def __init__(self):
        load_dotenv()
        self.pool = None
    
    async def init(self):
        self.pool = await asyncpg.create_pool(
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            database=os.getenv("POSTGRES_DB"),
            host="localhost",
            port=int(os.getenv("POSTGRES_PORT", 5432)),
            
        )
        print("✅ Подключение к базе прошло успешно")


async def main():
    db = DataBase()
    await db.init()
    courses_titles = ['A', 'B', 'C']
    for i in range(len(courses_titles)):
        await COURSES(db).add_courses(courses_titles[i])


if __name__ == "__main__":
    asyncio.run(main())
