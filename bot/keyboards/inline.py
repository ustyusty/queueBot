from telegram import InlineKeyboardButton, InlineKeyboardMarkup
class MainMenuKeyboard:
    @staticmethod
    def inline() -> InlineKeyboardMarkup:
        buttons = [
            [InlineKeyboardButton("Очередь на Императив", callback_data=f"GetCourseQueue:1")],
            [InlineKeyboardButton("Очередь на Машинки", callback_data=f"GetCourseQueue:2")],
            [InlineKeyboardButton("Очередь на Асик", callback_data=f"GetCourseQueue:35")]
        ]
        return InlineKeyboardMarkup(buttons)

class QueueListKeyboard:
    @staticmethod
    def is_list(queue_id: str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Я сдал!", callback_data=f"Done:{queue_id}")],
            [InlineKeyboardButton("Встать в очередь", callback_data=f"PutInQueue:{queue_id}")],
            [InlineKeyboardButton("Выйти из очереди", callback_data=f"LeaveFromQueue:{queue_id}")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_menu")]
        ])

    @staticmethod
    def not_list(queue_id: str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("Встать в очередь", callback_data=f"PutInQueue:{queue_id}")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_menu")]
        ])
    
    
class CommonKeyboard:
    @staticmethod
    def back_to_main() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_menu")]
        ])
