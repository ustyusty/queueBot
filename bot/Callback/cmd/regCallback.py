from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from bot.db import db
from bot.keyboards.inline import CommonKeyboard


class RegistrationHandler:
    def __init__(self, app: Application):
        self.app = app
        self.NAME, self.SURNAME = range(2)
        self._add_conv_handler()

    def _add_conv_handler(self):
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("register", self.startReg)],
            states={
                self.NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_name)],
                self.SURNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_surname)],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
            name="registerHandler",
        )
        self.app.add_handler(conv_handler)

    async def startReg(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("👋 Напиши своё имя:")
        return self.NAME

    async def get_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data["first_name"] = update.message.text.strip()
        await update.message.reply_text("Теперь напиши свою фамилию:")
        return self.SURNAME

    async def get_surname(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data["last_name"] = update.message.text.strip()
        user = update.effective_user

        await db.update_user(user, context.user_data["first_name"], context.user_data["last_name"])

        await update.message.reply_text(
            f"✅ Спасибо, {context.user_data['first_name']}! "
            "Вы успешно зарегистрированы.", reply_markup = CommonKeyboard.back_to_main()
        )

        context.user_data.clear()
        return ConversationHandler.END

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data.clear()
        await update.message.reply_text("❌ Регистрация отменена.")
        return ConversationHandler.END
