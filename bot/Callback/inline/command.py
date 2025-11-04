from bot.keyboards.inline import CommonKeyboard, QueueListKeyboard
from db.queue import QUEUE
from db.courses import COURSES
from db.get_user_info import USERINFO
from db.pack import PACK
class inlineCommand():
    def __init__(self, db):
        self.db = db
        self.queue = QUEUE(self.db) 
        self.cousrse = COURSES(self.db)
        self.pack = PACK(self.db)
        self.userinfo = USERINFO(self.db)

    async def put_on_queue(self, query, context):  # get in line
        course_title = context.user_data["step"]  # Extract course title from callback data
        course_id = await self.cousrse.get_course_id_by_title(course_title)  # Extract queue ID from callback data
        user_id = await self.userinfo.get_user_id(query.from_user.id)
        await self.queue.put_on_queue(user_id, course_id)
        await self.show_queue(query, context)

    async def set_done(self, query, context):  # mark as done
        course_title = context.user_data["step"]  # Extract course title from callback data
        user_id = await self.userinfo.get_user_id(query.from_user.id)
        course_id = await self.cousrse.get_course_id_by_title(course_title)
        await self.queue.set_is_pass(user_id, course_id)
        await self.show_queue(query, context)

    async def show_queue(self, query, context):  # show queue
        course_title = context.user_data["step"]  # Extract course title from callback data
        course_id = await self.cousrse.get_course_id_by_title(course_title)  # Extract queue ID from callback data
        rows = await self.queue.get_queue(course_id)
        print("Результат запроса:", *rows, sep="\n")
        if not rows:
            await query.edit_message_text("📭 Очередь пуста", reply_markup=QueueListKeyboard.not_list(course_title))
            return
        
        messages = []
        for i, r in enumerate(rows, 1):
            user_info = await self.userinfo.get_user_info(r['user_id'])

            if r['course_id'] != course_id:
                continue
            name = user_info.get('firstname')
            surname = user_info.get('surname')
            username = user_info.get('username')
            status = "✅" if r['is_pass'] else "⏳"

            messages.append(f"{i}. {status} {name} {surname if surname else '💩'} @{username}")
    
        queue_text = "📋 Очередь:\n" + "\n".join(messages)
        await query.edit_message_text(queue_text, reply_markup=QueueListKeyboard.is_list(course_title))

    async def leave_queue(self, query, context):
        course_title = context.user_data["step"]  # Extract course title from callback data
        course_id = await self.cousrse.get_course_id_by_title(course_title)
        user_id = await self.userinfo.get_user_id(query.from_user.id)
        await self.queue.leave_queue(user_id, course_id)
        await self.show_queue(query, context)