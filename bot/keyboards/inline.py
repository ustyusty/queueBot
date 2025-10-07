from telegram import InlineKeyboardButton, InlineKeyboardMarkup
class MainMenuKeyboard:
    @staticmethod
    def inline() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
                    [[InlineKeyboardButton("показать очередь", callback_data="show_queue")]]
                )
class QueueListKeyboard:
    @staticmethod
    def inline() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Я сдал!", callback_data="done")],
            [InlineKeyboardButton("Встать в очередь", callback_data="put_on_queue")],
            [InlineKeyboardButton("Выйти из очереди", callback_data="leave_queue")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_menu")]
        ])
class CommonKeyboard:
    @staticmethod
    def back_to_main() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_menu")]
        ])
