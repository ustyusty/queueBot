import logging

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from bot.routers import UserRepo
from bot.services.menu import show_main_menu
from bot.services.register import start as start_registration

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    repo: UserRepo | None = context.bot_data.get("UserRepo")
    if user is None or update.effective_message is None or repo is None:
        logger.error("Cannot process /start: user, message or UserRepo is missing")
        return ConversationHandler.END

    registered_user = await repo.get_user(user.id)
    if registered_user is not None:
        await update.effective_message.reply_text(
            f"👋 С возвращением, {registered_user['nicname']}!"
        )
        logger.info(
            "Registered user started bot: user_id=%s tg_id=%s",
            registered_user["id"],
            user.id,
        )
        await show_main_menu(update, context)
        return ConversationHandler.END

    await update.effective_message.reply_text(
        f"👋 Привет, {user.first_name or user.username}!"
    )
    logger.info("Starting registration: tg_id=%s", user.id)
    return await start_registration(update, context)


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    repo: UserRepo | None = context.bot_data.get("UserRepo")

    lines = [
        "Доступные команды:",
        "/start — зарегистрироваться и запустить бота",
        "/help — показать эту справку",
        "/change_group — сменить свою группу",
        "/cancel — отменить текущее действие",
    ]

    if user is not None and repo is not None and await repo.is_admin(user.id):
        lines.extend(
            [
                "",
                "Команды администратора:",
                "/add_group <название> — добавить группу",
                "/groups — показать группы",
                "/edit_group <ID> <название> — переименовать группу",
                "/delete_group <ID> — удалить группу",
                "/add_subject <название> — добавить предмет",
                "/subjects — показать предметы",
                "/edit_subject <ID> <название> — переименовать предмет",
                "/delete_subject <ID> — удалить предмет",
            ]
        )

    await update.message.reply_text("\n".join(lines))
    logger.debug("Help displayed: tg_id=%s", user.id if user is not None else None)
