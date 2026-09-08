import logging

from telegram import Update
from telegram.ext import ContextTypes

from bot.routers import UserRepo

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    repo: UserRepo = context.bot_data.get("UserRouter")
    await update.message.reply_text(f"👋 Привет, {user.first_name}!")
    user_id = await repo.register_user(user)
    logger.info("User registered or updated: user_id=%s tg_id=%s", user_id, user.id)


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    repo: UserRepo | None = context.bot_data.get("UserRouter")

    lines = [
        "Доступные команды:",
        "/start — зарегистрироваться и запустить бота",
        "/help — показать эту справку",
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
