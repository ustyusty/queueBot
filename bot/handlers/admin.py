import logging
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any

from telegram import Update
from telegram.ext import ContextTypes

from bot.routers import CourseRepo, GroupRepo, UserRepo
from database.exceptions import DatabaseQueryError

Handler = Callable[[Update, ContextTypes.DEFAULT_TYPE], Awaitable[None]]
logger = logging.getLogger(__name__)


def admin_only(handler: Handler) -> Handler:
    @wraps(handler)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        user_repo: UserRepo | None = context.bot_data.get("UserRouter")
        is_admin = (
            user is not None
            and user_repo is not None
            and await user_repo.is_admin(user.id)
        )
        if not is_admin:
            logger.warning(
                "Admin command rejected: command=%s tg_id=%s",
                handler.__name__,
                user.id if user is not None else None,
            )
            if update.effective_message is not None:
                await update.effective_message.reply_text(
                    "Эта команда доступна только администраторам."
                )
            return
        logger.info("Admin command started: command=%s tg_id=%s", handler.__name__, user.id)
        await handler(update, context)

    return wrapped


async def _reply(update: Update, text: str) -> None:
    if update.effective_message is not None:
        await update.effective_message.reply_text(text)


def _repo(context: ContextTypes.DEFAULT_TYPE, key: str) -> Any:
    repo = context.application.bot_data.get(key)
    if repo is None:
        raise RuntimeError(f"{key} is not initialized")
    return repo


def _title(args: list[str]) -> str:
    return " ".join(args).strip()


def _id_and_title(args: list[str]) -> tuple[int, str] | None:
    if len(args) < 2:
        return None
    try:
        item_id = int(args[0])
    except ValueError:
        return None
    title = _title(args[1:])
    return (item_id, title) if title else None


@admin_only
async def add_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    title = _title(context.args)
    if not title:
        await _reply(update, "Использование: /add_group <название группы>")
        return
    repo: GroupRepo = _repo(context, "GroupRepo")
    try:
        group = await repo.add_group(title)
    except DatabaseQueryError:
        logger.exception("Failed to add group: title=%r", title)
        await _reply(update, "Не удалось добавить группу. Возможно, название уже занято.")
        return
    logger.info("Group saved: group_id=%s title=%r", group["id"], group["title"])
    await _reply(update, f"Группа сохранена: {group['title']} (ID: {group['id']}).")


@admin_only
async def list_groups(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    repo: GroupRepo = _repo(context, "GroupRepo")
    groups = await repo.get_groups()
    if not groups:
        await _reply(update, "Групп пока нет.")
        return
    logger.info("Group list requested: count=%s", len(groups))
    lines = [f"{group['id']}. {group['title']}" for group in groups]
    await _reply(update, "Группы:\n" + "\n".join(lines))


@admin_only
async def edit_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    parsed = _id_and_title(context.args)
    if parsed is None:
        await _reply(update, "Использование: /edit_group <ID> <новое название>")
        return
    group_id, title = parsed
    repo: GroupRepo = _repo(context, "GroupRepo")
    try:
        group = await repo.update_group(group_id, title)
    except DatabaseQueryError:
        logger.exception("Failed to update group: group_id=%s title=%r", group_id, title)
        await _reply(update, "Не удалось переименовать группу. Возможно, название уже занято.")
        return
    if group is None:
        logger.warning("Cannot update group: group_id=%s not found", group_id)
        await _reply(update, f"Группа с ID {group_id} не найдена.")
        return
    logger.info("Group updated: group_id=%s title=%r", group_id, group["title"])
    await _reply(update, f"Группа переименована: {group['title']}.")


@admin_only
async def delete_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) != 1:
        await _reply(update, "Использование: /delete_group <ID>")
        return
    try:
        group_id = int(context.args[0])
    except ValueError:
        await _reply(update, "ID группы должен быть целым числом.")
        return
    repo: GroupRepo = _repo(context, "GroupRepo")
    group = await repo.delete_group(group_id)
    if group is None:
        logger.warning("Cannot delete group: group_id=%s not found", group_id)
        await _reply(update, f"Группа с ID {group_id} не найдена.")
        return
    logger.info("Group deleted: group_id=%s title=%r", group_id, group["title"])
    await _reply(update, f"Группа удалена: {group['title']}.")


@admin_only
async def add_course(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    title = _title(context.args)
    if not title:
        await _reply(update, "Использование: /add_course <название предмета>")
        return
    repo: CourseRepo = _repo(context, "CourseRepo")
    try:
        course = await repo.add_course(title)
    except DatabaseQueryError:
        logger.exception("Failed to add subject: title=%r", title)
        await _reply(update, "Не удалось добавить предмет. Возможно, название уже занято.")
        return
    logger.info("Subject saved: course_id=%s title=%r", course["id"], course["title"])
    await _reply(update, f"Предмет сохранён: {course['title']} (ID: {course['id']}).")


@admin_only
async def list_courses(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    repo: CourseRepo = _repo(context, "CourseRepo")
    courses = await repo.get_courses()
    if not courses:
        await _reply(update, "Предметов пока нет.")
        return
    logger.info("Subject list requested: count=%s", len(courses))
    lines = [f"{course['id']}. {course['title']}" for course in courses]
    await _reply(update, "Предметы:\n" + "\n".join(lines))


@admin_only
async def edit_course(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    parsed = _id_and_title(context.args)
    if parsed is None:
        await _reply(update, "Использование: /edit_course <ID> <новое название>")
        return
    course_id, title = parsed
    repo: CourseRepo = _repo(context, "CourseRepo")
    try:
        course = await repo.update_course(course_id, title)
    except DatabaseQueryError:
        logger.exception(
            "Failed to update subject: course_id=%s title=%r",
            course_id,
            title,
        )
        await _reply(update, "Не удалось переименовать предмет. Возможно, название уже занято.")
        return
    if course is None:
        logger.warning("Cannot update subject: course_id=%s not found", course_id)
        await _reply(update, f"Предмет с ID {course_id} не найден.")
        return
    logger.info("Subject updated: course_id=%s title=%r", course_id, course["title"])
    await _reply(update, f"Предмет переименован: {course['title']}.")


@admin_only
async def delete_course(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) != 1:
        await _reply(update, "Использование: /delete_course <ID>")
        return
    try:
        course_id = int(context.args[0])
    except ValueError:
        await _reply(update, "ID предмета должен быть целым числом.")
        return
    repo: CourseRepo = _repo(context, "CourseRepo")
    course = await repo.delete_course(course_id)
    if course is None:
        logger.warning("Cannot delete subject: course_id=%s not found", course_id)
        await _reply(update, f"Предмет с ID {course_id} не найден.")
        return
    logger.info("Subject deleted: course_id=%s title=%r", course_id, course["title"])
    await _reply(update, f"Предмет удалён: {course['title']}.")
