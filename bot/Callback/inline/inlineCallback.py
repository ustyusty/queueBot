from bot.keyboards.inline import CommonKeyboard, QueueListKeyboard
from telegram import Update
from telegram.ext import Application, CallbackQueryHandler, ContextTypes
from db.queue import QUEUE
from db.courses import COURSES
from db.get_user_info import USERINFO
from db.pack import PACK
from bot.keyboards.inline import MainMenuKeyboard
import logging
from bot.massages import main_menu
from bot.massages import queue as massage
from .mainhandler import main_handler as mh
from db.db import db

class InlineCallbackHandler():
    def __init__(self, app: Application):
        self.db = db
        self.app = app
        self.queue = QUEUE(self.db) 
        self.course = COURSES(self.db)
        self.pack = PACK(self.db)
        self.userinfo = USERINFO(self.db)
        self.app.add_handler(CallbackQueryHandler(mh.inline_callback))
    
        mh.register_callback(f"back_to_menu", self._back_to_menu)
        mh.register_callback(f"PutInQueue", self._put_in_queue)
        mh.register_callback(f"GetCourseQueue", self._show_queue)
        mh.register_callback(f"LeaveFromQueue", self._leave_queue)
        mh.register_callback(f"Done", self._set_done)

    async def _put_in_queue(self, query, course_id):  # get in line
        user_id = await self.userinfo.get_user_id(query.from_user.id)

        if user_id is None:
            await query.edit_message_text("❗ Сначала зарегистрируйтесь с помощью команды /register")
            return
        
        await self.queue.put_in_queue(user_id, course_id)
        await self._show_queue(query, course_id)


    async def _set_done(self, query, course_id):  # mark as done
        user_id = await self.userinfo.get_user_id(query.from_user.id)
        await self.queue.set_is_pass(user_id, course_id)
        await self._show_queue(query, course_id)

    async def _show_queue(self, query, course_id):  # show queue
        rows = await self.queue.get_queue(course_id)

        list_of_qeue = await massage.create_massage(rows, self.userinfo, QueueListKeyboard)
        await query.edit_message_text(list_of_qeue["mes"], reply_markup=list_of_qeue["func"](course_id))

    async def _leave_queue(self, query, course_id):
        user_id = await self.userinfo.get_user_id(query.from_user.id)
        await self.queue.leave_queue(user_id, course_id)
        await self._show_queue(query, course_id)

    async def _back_to_menu(self, query):
        await query.edit_message_text(main_menu.text, reply_markup=MainMenuKeyboard.inline())