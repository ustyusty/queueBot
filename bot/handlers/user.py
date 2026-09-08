from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from bot.handlers.starting import start
from bot.services.menu import (
    BACK_CALLBACK_DATA,
    COURSE_CALLBACK_PREFIX,
    DONE_CALLBACK_PREFIX,
    JOIN_CALLBACK_PREFIX,
    menu_callback,
)
from bot.services.register import (
    GROUP,
    GROUP_CALLBACK_PREFIX,
    NICKNAME,
    cancel,
    change_group,
    group,
    nickname,
)


def registration_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("change_group", change_group),
        ],
        states={
            NICKNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, nickname)],
            GROUP: [
                CallbackQueryHandler(
                    group,
                    pattern=rf"^{GROUP_CALLBACK_PREFIX}\d+$",
                )
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )


def main_menu_handler() -> CallbackQueryHandler:
    return CallbackQueryHandler(
        menu_callback,
        pattern=(
            rf"^(?:{COURSE_CALLBACK_PREFIX}\d+|"
            rf"{JOIN_CALLBACK_PREFIX}\d+|{DONE_CALLBACK_PREFIX}\d+|"
            rf"{BACK_CALLBACK_DATA})$"
        ),
    )
