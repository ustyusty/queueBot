import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.routers import CourseRepo, QueueRepo, UserRepo

logger = logging.getLogger(__name__)

COURSE_CALLBACK_PREFIX = "queue_course:"
JOIN_CALLBACK_PREFIX = "queue_join:"
DONE_CALLBACK_PREFIX = "queue_done:"
BACK_CALLBACK_DATA = "queue_back"

MENU_TEXT = (
    "🎓✨ <b>QueueBot — очередь без суеты!</b>\n\n"
    "Здесь не нужно караулить преподавателя у двери и выяснять, кто за кем 😌\n"
    "Выбирай предмет — и я покажу текущую очередь.\n\n"
    "👇 <b>Какой предмет смотрим?</b>"
)


async def show_main_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    edit: bool = False,
) -> None:
    course_repo: CourseRepo | None = context.bot_data.get("CourseRepo")
    message = update.effective_message
    if course_repo is None or message is None:
        logger.error("Cannot show main menu: CourseRepo or message is missing")
        return

    courses = await course_repo.get_courses()
    if courses:
        buttons = [
            InlineKeyboardButton(
                f"📚 {course['title']}",
                callback_data=f"{COURSE_CALLBACK_PREFIX}{course['id']}",
            )
            for course in courses
        ]
        keyboard = InlineKeyboardMarkup(
            [buttons[index:index + 1] for index in range(0, len(buttons), 1)]
        )
        text = MENU_TEXT
    else:
        keyboard = None
        text = "🎓 <b>QueueBot</b>\n\nПока нет доступных предметов. Загляни чуть позже 👀"

    if edit and update.callback_query is not None:
        await update.callback_query.edit_message_text(
            text,
            reply_markup=keyboard,
            parse_mode="HTML",
        )
    else:
        await message.reply_text(text, reply_markup=keyboard, parse_mode="HTML")
    logger.info("Main menu displayed: courses=%s", len(courses))


def _callback_id(data: str | None, prefix: str) -> int | None:
    if data is None or not data.startswith(prefix):
        return None
    try:
        return int(data.removeprefix(prefix))
    except ValueError:
        return None


def _short(value: object | None, limit: int) -> str:
    text = str(value or "").replace("\n", " ").strip()
    return text if len(text) <= limit else text[:limit - 1] + "…"


async def _render_queue(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    course_id: int,
    *,
    notice: str | None = None,
) -> None:
    query = update.callback_query
    telegram_user = update.effective_user
    user_repo: UserRepo | None = context.bot_data.get("UserRepo")
    course_repo: CourseRepo | None = context.bot_data.get("CourseRepo")
    queue_repo: QueueRepo | None = context.bot_data.get("QueueRepo")
    if query is None or telegram_user is None:
        return
    if user_repo is None or course_repo is None or queue_repo is None:
        logger.error("Cannot render queue: repository is missing")
        await query.edit_message_text("Сервис временно недоступен.")
        return

    user = await user_repo.get_user(telegram_user.id)
    if user is None:
        await query.edit_message_text("Сначала выполни /start и зарегистрируйся.")
        return
    course = await course_repo.get_course(course_id)
    if course is None:
        await query.edit_message_text(
            "Этот предмет больше недоступен.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("⬅️ Назад", callback_data=BACK_CALLBACK_DATA)]]
            ),
        )
        return

    entries = await queue_repo.get_queue_entries(
        course_id=course_id,
        group_id=user["group_id"],
        only_active=True,
    )
    lines = [f"📚 Очередь: {_short(course['title'], 80)}", ""]
    if notice:
        lines.extend([notice, ""])
    if entries:
        for position, entry in enumerate(entries[:25], start=1):
            nicname = _short(entry["nicname"], 80) or "Без имени"
            username = _short(entry["username"], 40)
            username_text = f"@{username}" if username else "без username"
            marker = " 👈" if entry["user_id"] == user["id"] else ""
            lines.append(f"{position}. {nicname} — {username_text}{marker}")
        if len(entries) > 25:
            lines.append(f"…и ещё {len(entries) - 25}")
    else:
        lines.append("Очередь пока пуста. Можешь быть первым! 🚀")

    already_joined = any(entry["user_id"] == user["id"] for entry in entries)
    buttons = []
    if already_joined:
        buttons.append(
            [
                InlineKeyboardButton(
                    "✅ Я всё",
                    callback_data=f"{DONE_CALLBACK_PREFIX}{course_id}",
                )
            ]
        )
    else:
        buttons.append(
            [InlineKeyboardButton("➕ Встать в очередь", callback_data=f"{JOIN_CALLBACK_PREFIX}{course_id}")]
        )
    buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data=BACK_CALLBACK_DATA)])
    await query.edit_message_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(buttons),
    )
    logger.info(
        "Queue displayed: course_id=%s group_id=%s entries=%s",
        course_id,
        user["group_id"],
        len(entries),
    )


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None:
        return
    data = query.data

    if data == BACK_CALLBACK_DATA:
        await query.answer()
        await show_main_menu(update, context, edit=True)
        return

    course_id = _callback_id(data, COURSE_CALLBACK_PREFIX)
    if course_id is not None:
        await query.answer()
        await _render_queue(update, context, course_id)
        return

    join_course_id = _callback_id(data, JOIN_CALLBACK_PREFIX)
    done_course_id = _callback_id(data, DONE_CALLBACK_PREFIX)
    if join_course_id is None and done_course_id is None:
        logger.warning("Invalid menu callback received: data=%r", data)
        await query.answer("Не удалось обработать кнопку.", show_alert=True)
        return
    course_id = join_course_id if join_course_id is not None else done_course_id

    user_repo: UserRepo | None = context.bot_data.get("UserRepo")
    queue_repo: QueueRepo | None = context.bot_data.get("QueueRepo")
    telegram_user = update.effective_user
    if user_repo is None or queue_repo is None or telegram_user is None:
        logger.error("Cannot update queue: repository or user is missing")
        await query.answer("Сервис временно недоступен.", show_alert=True)
        return

    user = await user_repo.get_user(telegram_user.id)
    if user is None:
        await query.answer("Сначала выполни /start.", show_alert=True)
        return

    await query.answer()
    if done_course_id is not None:
        finished_entry = await queue_repo.finish_queue_entry(user["id"], course_id)
        notice = (
            "✅ Готово! Ты вышел из очереди."
            if finished_entry is not None
            else "ℹ️ Тебя уже нет в этой очереди."
        )
        logger.info(
            "Queue finish handled: user_id=%s course_id=%s finished=%s",
            user["id"],
            course_id,
            finished_entry is not None,
        )
    else:
        entry, created = await queue_repo.join_queue(user["id"], course_id)
        position = await queue_repo.get_queue_position(entry["id"])
        notice = (
            f"✅ Ты в очереди! Твоя позиция: {position}."
            if created
            else f"ℹ️ Ты уже в очереди. Твоя позиция: {position}."
        )
        logger.info(
            "Queue join handled: user_id=%s course_id=%s created=%s position=%s",
            user["id"],
            course_id,
            created,
            position,
        )
    await _render_queue(update, context, course_id, notice=notice)
