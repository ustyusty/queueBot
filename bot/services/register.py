import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

from bot.routers import GroupRepo, UserRepo
from bot.services.menu import show_main_menu

logger = logging.getLogger(__name__)

NICKNAME, GROUP = range(2)
GROUP_CALLBACK_PREFIX = "registration_group:"


def build_inline_keyboard(
    buttons_data: list[tuple[str, str]],
    columns: int = 2,
) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text, callback_data=callback)
            for text, callback in buttons_data[index:index + columns]
        ]
        for index in range(0, len(buttons_data), columns)
    ]
    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    context.user_data["registration_mode"] = "register"
    await update.effective_message.reply_text(
        "Давай зарегистрируемся. Как к тебе обращаться?"
    )
    return NICKNAME


async def nickname(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    value = (update.effective_message.text or "").strip()
    if not value:
        await update.effective_message.reply_text("Имя не может быть пустым. Попробуй ещё раз.")
        return NICKNAME
    if len(value) > 255:
        await update.effective_message.reply_text("Имя слишком длинное. Максимум 255 символов.")
        return NICKNAME

    context.user_data["registration_nicname"] = value
    return await _show_groups(update, context)


async def change_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    user_repo: UserRepo | None = context.bot_data.get("UserRepo")
    if user is None or user_repo is None:
        logger.error("Cannot change group: user or UserRepo is missing")
        return ConversationHandler.END

    registered_user = await user_repo.get_user(user.id)
    if registered_user is None:
        await update.effective_message.reply_text(
            "Сначала зарегистрируйся с помощью команды /start."
        )
        return ConversationHandler.END

    context.user_data.clear()
    context.user_data["registration_mode"] = "change_group"
    logger.info("Group change started: user_id=%s tg_id=%s", registered_user["id"], user.id)
    return await _show_groups(update, context)


async def _show_groups(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    group_repo: GroupRepo | None = context.bot_data.get("GroupRepo")
    if group_repo is None:
        logger.error("Cannot show groups: GroupRepo is missing")
        await update.effective_message.reply_text("Сервис временно недоступен.")
        return ConversationHandler.END

    groups = await group_repo.get_groups()
    if not groups:
        await update.effective_message.reply_text(
            "Пока нет доступных групп. Обратись к администратору."
        )
        logger.warning("Registration cannot continue: no groups found")
        return ConversationHandler.END

    buttons = [
        (group["title"], f"{GROUP_CALLBACK_PREFIX}{group['id']}")
        for group in groups
    ]
    await update.effective_message.reply_text(
        "Выбери группу, в которой ты учишься:",
        reply_markup=build_inline_keyboard(buttons),
    )
    return GROUP


async def group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    user = update.effective_user
    if query is None or user is None:
        return ConversationHandler.END

    await query.answer()
    try:
        group_id = int(query.data.removeprefix(GROUP_CALLBACK_PREFIX))
    except (AttributeError, ValueError):
        logger.warning("Invalid group callback received: data=%r", query.data)
        await query.edit_message_text("Не удалось определить группу. Попробуй снова.")
        return ConversationHandler.END

    group_repo: GroupRepo | None = context.bot_data.get("GroupRepo")
    user_repo: UserRepo | None = context.bot_data.get("UserRepo")
    if group_repo is None or user_repo is None:
        logger.error("Cannot save selected group: repository is missing")
        await query.edit_message_text("Сервис временно недоступен.")
        return ConversationHandler.END

    selected_group = await group_repo.get_group(group_id)
    if selected_group is None:
        logger.warning("Selected group no longer exists: group_id=%s", group_id)
        await query.edit_message_text("Эта группа больше недоступна. Запусти команду ещё раз.")
        return ConversationHandler.END

    if context.user_data.get("registration_mode") == "change_group":
        changed_user = await user_repo.change_group(user.id, group_id)
        if changed_user is None:
            await query.edit_message_text("Пользователь не найден. Выполни /start.")
            return ConversationHandler.END
        logger.info("User group changed: user_id=%s group_id=%s", changed_user["id"], group_id)
        await query.edit_message_text(f"Группа изменена на «{selected_group['title']}».")
    else:
        nicname = context.user_data.get("registration_nicname")
        if not nicname:
            await query.edit_message_text("Регистрация устарела. Выполни /start ещё раз.")
            return ConversationHandler.END
        user_id = await user_repo.register_user(user, nicname, group_id)
        logger.info("User registered: user_id=%s tg_id=%s group_id=%s", user_id, user.id, group_id)
        await query.edit_message_text(
            f"Регистрация завершена. Твоя группа — «{selected_group['title']}»."
        )

    context.user_data.clear()
    await show_main_menu(update, context)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    context.user_data.clear()
    logger.info("Registration flow cancelled: tg_id=%s", user.id if user else None)
    await update.effective_message.reply_text("Действие отменено.")
    return ConversationHandler.END
