from telegram import InlineKeyboardButton, InlineKeyboardMarkup
class MainMenuKeyboard:
    @staticmethod
    def inline() -> InlineKeyboardMarkup:
        buttons = [
            [InlineKeyboardButton("Очередь A", callback_data="show_queue_A")],
            [InlineKeyboardButton("Очередь B", callback_data="show_queue_B")],
            [InlineKeyboardButton("Очередь C", callback_data="show_queue_C")]
        ]
        return InlineKeyboardMarkup(buttons)

class QueueListKeyboard:
    @staticmethod
    def is_list(queue_id: str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Я сдал!", callback_data=f"done_{queue_id}")],
            [InlineKeyboardButton("Встать в очередь", callback_data=f"put_on_queue_{queue_id}")],
            [InlineKeyboardButton("Выйти из очереди", callback_data=f"leave_queue_{queue_id}")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_menu")]
        ])

    @staticmethod
    def not_list(queue_id: str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("Встать в очередь", callback_data=f"put_on_queue_{queue_id}")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_menu")]
        ])
    
    
class CommonKeyboard:
    @staticmethod
    def back_to_main() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_menu")]
        ])
