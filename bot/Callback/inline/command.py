from bot.keyboards.inline import CommonKeyboard, QueueListKeyboard
class inlineCommand():
    def __init__(self, db):
        self.db = db

    async def put_on_queue(self, query):
        await self.db.put_on_queue(query.from_user)
        await self.show_queue(query)
    
    async def set_done(self, query):
        await self.db.set_done_is_pass(query.from_user)
        await self.show_queue(query)

    async def show_queue(self, query):
        rows = await self.db.get_queue()

        if not rows:
            await query.edit_message_text("📭 Очередь пуста", reply_markup = CommonKeyboard.back_to_main())
            return
        
        messages = []
        for i, r in enumerate(rows, 1):
            user_info = await self.db.get_user_info(r['user_id'])
            name = user_info.get('first_name')
            surname = user_info.get('last_name')
            username = user_info.get('username')
            status = "✅" if r.get('is_pass') else "⏳"
            
            messages.append(f"{i}. {status} {name} {surname if surname else '💩'} @{username}")
    
        queue_text = "📋 Очередь:\n" + "\n".join(messages)
        await query.edit_message_text(queue_text, reply_markup = QueueListKeyboard.inline())
    
    async def leave_queue(self, query):
        await self.db.leave_queue(query.from_user)
        await self.show_queue(query)