from db.db import db
from db.add_user import ADDUSER
from db.get_user_info import USERINFO
from db.courses import COURSES
from db.pack import PACK
from db.queue import QUEUE
from db.group import GROUP
import asyncio
import datetime


class User:
    def __init__(self, id, username = None, firstname=None, surname=None, group = None):
        self.id = id
        self.username = username
        self.firstname = firstname
        self.lastname = surname
        self.group = group
    
class Pack:
    def __init__(self, ):
        pass

async def main():
    await db.init()

    # user = User(id = 7347273, firstname="Нта", surname="Никиич", group="47")
    # adduser = ADDUSER(user)
    # await adduser.register_user()

    # userinfo = USERINFO()
    # info = await userinfo.GUI(7347273)

    # await COURSES().add_courses("imper")

    # await PACK().add_pack("5", datetime.date(2025, 10, 29), "imper")
    # pack_id = await PACK().get_pack("5")

    # await QUEUE().put_on_queue(info["id"], pack_id, 10)
    a = await QUEUE().get_queue()
    for row in a:
        print(row)
    
    await db.close()


if __name__ == "__main__":
    asyncio.run(main())
