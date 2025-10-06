from telegram import  ReplyKeyboardMarkup
class CommonKeyboard:
    @staticmethod
    def back_to_main() -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup([["/main"]] , resize_keyboard=True)