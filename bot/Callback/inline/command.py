from bot.keyboards.inline import CommonKeyboard, QueueListKeyboard
from db.queue import QUEUE
from db.courses import COURSES
from db.get_user_info import USERINFO
from db.pack import PACK
class inlineCommand():
    def __init__(self, db, pack_id):
        self.db = db
        self.pack_id = pack_id
        self.courses_id =COURSES().get_courses_id_by_pack(pack_id)  # get course_id by pack_id, it needs to show queue for specific course

    async def put_on_queue(self, query, context):  # get in line
        course_title = context.user_data["step"]  # Extract course title from callback data
        course_id = await COURSES().get_course_id_by_title(course_title)  # Extract queue ID from callback data
        user_id = await USERINFO().get_user_id(query.from_user.id)
        await QUEUE().put_on_queue(user_id, course_id, priority=0)
        await self.show_queue(query, context)

    async def set_done(self, query, context):  # mark as done
        course_title = context.user_data["step"]  # Extract course title from callback data
        course_id = await COURSES().get_course_id_by_title(course_title)  # Extract queue ID from callback data
        await QUEUE().set_is_pass(query.from_user.id, course_id)
        await self.show_queue(query, context)

    async def show_queue(self, query, context):  # show queue
        course_title = context.user_data["step"]  # Extract course title from callback data
        course_id = await COURSES().get_course_id_by_title(course_title)  # Extract queue ID from callback data
        rows = await QUEUE().get_queue(course_id)

        if not rows:
            await query.edit_message_text("📭 Очередь пуста", reply_markup=QueueListKeyboard.not_list(course_title))
            return
        
        messages = []
        for i, r in enumerate(rows, 1):
            user_info = await USERINFO().get_user_info(r['user_id'])
            name = user_info.get('firstname')
            surname = user_info.get('surname')
            username = user_info.get('username')
            status = "✅" if user_info.get('is_pass') else "⏳"
            
            messages.append(f"{i}. {status} {name} {surname if surname else '💩'} @{username}")
    
        queue_text = "📋 Очередь:\n" + "\n".join(messages)
        await query.edit_message_text(queue_text, reply_markup=QueueListKeyboard.is_list(course_title))

    async def leave_queue(self, query, context):
        course_title = context.user_data["step"]  # Extract course title from callback data
        pack_id = await PACK().get_pack_id_by_title(course_title)
        await QUEUE().leave_queue(query.from_user.id, pack_id)
        await self.show_queue(query, context)