from telegram import InlineKeyboardButton, InlineKeyboardMarkup
class MainMenuKeyboard:
    @staticmethod
    def inline() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
                    [[InlineKeyboardButton("встать в очередь", callback_data="put_on_queue")],
                    [InlineKeyboardButton("показать очередь", callback_data="show_queue")],
                    [InlineKeyboardButton("выйти из очереди", callback_data="leave_queue")]]
                )
class CommonKeyboard:
    @staticmethod
    def back_to_main() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_menu")]
        ])
