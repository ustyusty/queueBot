import logging
from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo

from telegram import InlineKeyboardButton as Button, InlineKeyboardMarkup as Keyboard
from telegram.ext import CallbackQueryHandler, CommandHandler, ConversationHandler, MessageHandler, filters

from database.exceptions import DatabaseQueryError
from bot.services.deadline import date_choices, month_keyboard, time_keyboard

logger = logging.getLogger(__name__)
LOCAL_TIME = ZoneInfo('Asia/Novosibirsk')
COURSE, TITLE, DESCRIPTION, DEADLINE, FILE, CONFIRM, QUESTION, ANSWER = range(20, 28)
PRESENTATION_QUESTIONS = 28
LABELS = {'homework': '📝 Домашние задания', 'presentation': '🎤 Презентации'}


async def user_for(update, context):
    user = await context.bot_data['UserRepo'].get_user(update.effective_user.id)
    if user is None or user['group_id'] is None:
        await update.effective_message.reply_text('Сначала зарегистрируйся и выбери группу: /start.')
        return None
    return user


async def send(update, text, buttons=None, *, file_id=None, file_type='document'):
    markup = Keyboard(buttons) if buttons else None
    message = update.effective_message
    current_media = message.photo or message.document
    if file_id:
        # Telegram captions are limited to 1024 UTF-16 code units.
        fits_caption = len(text.encode('utf-16-le')) // 2 <= 1024
        current_id = (message.photo[-1].file_id if message.photo else
                      message.document.file_id if message.document else None)
        if update.callback_query and current_id == file_id and fits_caption:
            await update.callback_query.edit_message_caption(caption=text, reply_markup=markup)
            return
        sender = message.reply_photo if file_type == 'photo' else message.reply_document
        await sender(file_id, caption=text if fits_caption else None,
                     reply_markup=markup if fits_caption else None)
        if not fits_caption:
            await message.reply_text(text, reply_markup=markup)
        if update.callback_query:
            await update.callback_query.edit_message_reply_markup(reply_markup=None)
    elif update.callback_query and current_media:
        await message.reply_text(text, reply_markup=markup)
        await update.callback_query.edit_message_reply_markup(reply_markup=None)
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=markup)
    else:
        await update.effective_message.reply_text(text, reply_markup=markup)


def date_text(value):
    return value.astimezone(LOCAL_TIME).strftime('%d.%m.%Y %H:%M') if value else 'Без срока'


async def show_list(update, context, kind, page=0):
    user = await user_for(update, context)
    if user is None:
        return
    items = await context.bot_data['AssignmentRepo'].list(user['group_id'], kind)
    page = max(0, min(page, (len(items) - 1) // 10))
    buttons = [[Button(f"{item['course_title'][:30]} · {item['title'][:40]}", callback_data=f"study:view:{item['id']}")]
               for item in items[page * 10:(page + 1) * 10]]
    nav = []
    if page:
        nav.append(Button('◀️', callback_data=f'study:list:{kind}:{page-1}'))
    if (page + 1) * 10 < len(items):
        nav.append(Button('▶️', callback_data=f'study:list:{kind}:{page+1}'))
    if nav:
        buttons.append(nav)
    if kind == 'presentation' or user['is_admin']:
        buttons.append([Button('➕ Добавить', callback_data=f'study:new:{kind}')])
    buttons.append([Button('⬅️ Главное меню', callback_data='queue_back')])
    await send(update, LABELS[kind] + ('\n\nВыбери задание:' if items else '\n\nПока здесь пусто.'), buttons)


async def show_item(update, context, item):
    user = await user_for(update, context)
    if user is None:
        return
    repo = context.bot_data['AssignmentRepo']
    text = (f"{LABELS[item['kind']]}\n📚 {item['course_title'][:100]}\n\n{item['title']}\n"
            f"📅 {date_text(item['deadline'])} (Новосибирск)\n\n{item['description']}")
    buttons = []
    if item['file_id'] and item['kind'] != 'homework':
        buttons.append([Button('📎 Скачать файл', callback_data=f"study:file:{item['id']}")])
    if item['kind'] == 'homework':
        text += '\n\n✅ Выполнено' if item['completed'] else '\n\n⬜ Ещё не выполнено'
        action = 'undo' if item['completed'] else 'done'
        buttons.append([Button('↩️ Снять отметку' if item['completed'] else '✅ Выполнено', callback_data=f"study:{action}:{item['id']}")])
    else:
        questions = await repo.questions(item['id'])
        text += f'\n\n❓ Подготовленных вопросов: {len(questions)}'
        if questions:
            buttons.append([Button('❓ Вопросы и ответы', callback_data=f"study:questions:{item['id']}:0")])
        if item['questions_text']:
            buttons.append([Button('📝 Вопросы автора', callback_data=f"study:qtext:{item['id']}")])
        if item['questions_file_id']:
            buttons.append([Button('📎 Файл с вопросами', callback_data=f"study:qfile:{item['id']}")])
        if user['is_admin'] or item['author_id'] == user['id']:
            buttons.append([Button('➕ Добавить вопрос', callback_data=f"study:question:{item['id']}")])
    if user['is_admin'] or item['author_id'] == user['id']:
        buttons.append([Button('🗑 Удалить', callback_data=f"study:delete:{item['id']}")])
    buttons.append([Button('⬅️ К списку', callback_data=f"study:list:{item['kind']}:0")])
    if item['kind'] == 'homework':
        await send(update, text, buttons, file_id=item['file_id'], file_type=item['file_type'])
    else:
        await send(update, text, buttons)


async def callback(update, context):
    query = update.callback_query
    await query.answer()
    parts = query.data.split(':')
    action = parts[1]
    if action == 'list':
        await show_list(update, context, parts[2], int(parts[3]))
        return
    user = await user_for(update, context)
    if user is None:
        return
    repo = context.bot_data['AssignmentRepo']
    item = await repo.get(int(parts[2]), user['group_id'], user['id'])
    if item is None:
        await send(update, 'Задание не найдено или недоступно твоей группе.', [[Button('⬅️ Главное меню', callback_data='queue_back')]])
        return
    can_edit = user['is_admin'] or item['author_id'] == user['id']
    if action in ('delete', 'remove'):
        if not can_edit:
            await update.effective_message.reply_text('Удалить задание может автор или администратор.')
            return
        if action == 'delete':
            await send(update, f"Удалить «{item['title']}» и связанные данные?", [
                [Button('Да, удалить', callback_data=f"study:remove:{item['id']}")],
                [Button('Отмена', callback_data=f"study:view:{item['id']}")]])
            return
        await repo.delete(item['id'])
        await show_list(update, context, item['kind'])
        return
    if action in ('done', 'undo') and item['kind'] == 'homework':
        await repo.complete(item['id'], user['id'], action == 'done')
        item = await repo.get(item['id'], user['group_id'], user['id'])
    if action == 'file' and item['file_id']:
        sender = update.effective_message.reply_photo if item['file_type'] == 'photo' else update.effective_message.reply_document
        await sender(item['file_id'])
        return
    if action == 'qfile' and item['kind'] == 'presentation' and item['questions_file_id']:
        await update.effective_message.reply_document(item['questions_file_id'], caption='❓ Вопросы к презентации')
        return
    if action == 'qtext' and item['kind'] == 'presentation' and item['questions_text']:
        await send(update, '❓ Вопросы автора\n\n' + item['questions_text'],
                   [[Button('⬅️ К презентации', callback_data=f"study:view:{item['id']}")]])
        return
    if action == 'questions' and item['kind'] == 'presentation':
        questions = await repo.questions(item['id'])
        if questions:
            index = max(0, min(int(parts[3]), len(questions) - 1))
            question = questions[index]
            nav = []
            if index:
                nav.append(Button('◀️', callback_data=f"study:questions:{item['id']}:{index-1}"))
            if index + 1 < len(questions):
                nav.append(Button('▶️', callback_data=f"study:questions:{item['id']}:{index+1}"))
            buttons = [nav] if nav else []
            buttons.append([Button('⬅️ К презентации', callback_data=f"study:view:{item['id']}")])
            await send(update, f"❓ Вопрос {index+1}/{len(questions)}\n\n{question['question']}\n\n💡 Ответ:\n{question['answer']}", buttons)
            return
    await show_item(update, context, item)


async def begin(update, context):
    user = await user_for(update, context)
    if user is None:
        return ConversationHandler.END
    if update.callback_query:
        await update.callback_query.answer()
        kind = update.callback_query.data.split(':')[2]
    else:
        kind = 'homework' if update.effective_message.text.split()[0].split('@')[0] == '/add_homework' else 'presentation'
    if kind == 'homework' and not user['is_admin']:
        await update.effective_message.reply_text('Домашние задания добавляет администратор.')
        return ConversationHandler.END
    courses = await context.bot_data['CourseRepo'].get_courses()
    if not courses:
        await update.effective_message.reply_text('Сначала администратор должен добавить предметы.')
        return ConversationHandler.END
    context.user_data['study_draft'] = {'kind': kind}
    await update.effective_message.reply_text('Выбери предмет. Публикация будет для твоей группы. Отмена: /cancel.',
        reply_markup=Keyboard([[Button(c['title'][:100], callback_data=f"study:course:{c['id']}")] for c in courses]))
    return COURSE


async def choose_course(update, context):
    await update.callback_query.answer()
    course_id = int(update.callback_query.data.split(':')[2])
    if await context.bot_data['CourseRepo'].get_course(course_id) is None:
        await update.effective_message.reply_text('Предмет удалён. Выбери другой.')
        return COURSE
    context.user_data['study_draft']['course_id'] = course_id
    await update.effective_message.reply_text('Напиши название (до 150 символов).')
    return TITLE


async def title(update, context):
    value = update.effective_message.text.strip()
    if not 1 <= len(value) <= 150:
        await update.effective_message.reply_text('Нужно название от 1 до 150 символов.')
        return TITLE
    context.user_data['study_draft']['title'] = value
    await update.effective_message.reply_text('Напиши описание задания или презентации (до 2500 символов).')
    return DESCRIPTION


async def description(update, context):
    value = update.effective_message.text.strip()
    if not 1 <= len(value) <= 2500:
        await update.effective_message.reply_text('Описание должно содержать от 1 до 2500 символов.')
        return DESCRIPTION
    context.user_data['study_draft']['description'] = value
    await update.effective_message.reply_text('Выбери срок / дату выступления. Время — Новосибирск.\nМожно также написать ДД.ММ.ГГГГ ЧЧ:ММ.', reply_markup=date_choices())
    return DEADLINE


async def ask_attachment(update, context):
    presentation = context.user_data['study_draft'].get('kind') == 'presentation'
    await update.effective_message.reply_text(
        'Загрузи свою презентацию документом (например PPTX или PDF).'
        if presentation else 'Прикрепи документ или фото, либо нажми /skip.')
    return FILE


async def deadline_callback(update, context):
    await update.callback_query.answer()
    parts = update.callback_query.data.split(':')
    action = parts[2]
    draft = context.user_data['study_draft']
    today = datetime.now(LOCAL_TIME).date()
    if action == 'noop':
        return DEADLINE
    if action == 'none':
        draft['deadline'] = None
        await update.callback_query.edit_message_reply_markup(reply_markup=None)
        return await ask_attachment(update, context)
    if action in ('calendar', 'month'):
        year, month = (int(parts[3]), int(parts[4])) if action == 'month' else (today.year, today.month)
        if not 2 <= year <= 9998 or not 1 <= month <= 12:
            return DEADLINE
        await update.callback_query.edit_message_text('📅 Выбери дату:', reply_markup=month_keyboard(year, month))
        return DEADLINE
    if action in ('today', 'tomorrow', 'day'):
        try:
            selected = date.fromisoformat(parts[3]) if action == 'day' else today + timedelta(days=action == 'tomorrow')
        except ValueError:
            return DEADLINE
        draft['selected_date'] = selected
        await update.callback_query.edit_message_text(
            f"📅 {selected.strftime('%d.%m.%Y')}\nВыбери время (Новосибирск):", reply_markup=time_keyboard())
        return DEADLINE
    if action == 'custom':
        await update.effective_message.reply_text('Напиши время в формате ЧЧ:ММ, например 14:30.')
        return DEADLINE
    if action == 'time' and draft.get('selected_date'):
        try:
            selected_time = time.fromisoformat(':'.join(parts[3:]))
        except ValueError:
            return DEADLINE
        draft['deadline'] = datetime.combine(draft['selected_date'], selected_time, LOCAL_TIME)
        await update.callback_query.edit_message_reply_markup(reply_markup=None)
        return await ask_attachment(update, context)
    return DEADLINE


async def deadline(update, context):
    value = update.effective_message.text
    try:
        if value.split('@')[0] == '/skip':
            parsed = None
        elif context.user_data['study_draft'].get('selected_date') and len(value.strip()) == 5:
            parsed = datetime.combine(context.user_data['study_draft']['selected_date'],
                                      datetime.strptime(value.strip(), '%H:%M').time(), LOCAL_TIME)
        else:
            parsed = datetime.strptime(value.strip(), '%d.%m.%Y %H:%M').replace(tzinfo=LOCAL_TIME)
    except ValueError:
        await update.effective_message.reply_text('Пример: 20.10.2026 23:59. Без срока: /skip.')
        return DEADLINE
    context.user_data['study_draft']['deadline'] = parsed
    return await ask_attachment(update, context)


async def attachment(update, context):
    draft = context.user_data['study_draft']
    message = update.effective_message
    if draft['kind'] == 'presentation' and not message.document:
        await message.reply_text('Для презентации нужен документ. Загрузи PPTX, PDF или другой файл.')
        return FILE
    draft['file_type'] = 'photo' if message.photo else 'document'
    draft['file_id'] = (message.photo[-1].file_id if message.photo else
                        message.document.file_id if message.document else None)
    if draft['kind'] == 'presentation':
        await message.reply_text('Теперь отправь подготовленные вопросы (можно вместе с ответами) одним текстовым сообщением или отдельным файлом. Текст — до 3500 символов.')
        return PRESENTATION_QUESTIONS
    return await confirm(update, context)


async def presentation_questions(update, context):
    draft = context.user_data['study_draft']
    message = update.effective_message
    if message.document:
        draft['questions_file_id'] = message.document.file_id
        draft['questions_text'] = None
    else:
        value = (message.text or '').strip()
        if not 1 <= len(value.encode('utf-16-le')) // 2 <= 3500:
            await message.reply_text('Отправь вопросы текстом от 1 до 3500 символов или документом.')
            return PRESENTATION_QUESTIONS
        draft['questions_text'] = value
        draft['questions_file_id'] = None
    return await confirm(update, context)


async def confirm(update, context):
    draft = context.user_data['study_draft']
    questions_notice = ('❓ Вопросы добавлены ' + ('файлом' if draft.get('questions_file_id') else 'текстом') + '\n\n') if draft['kind'] == 'presentation' else ''
    await update.effective_message.reply_text(
        f"{LABELS[draft['kind']]}\n\n{draft['title']}\n📅 {date_text(draft['deadline'])}\n\n{draft['description']}\n\n"
        + ('📎 Файл прикреплён\n\n' if draft['file_id'] else '') + questions_notice + 'Опубликовать для твоей группы?',
        reply_markup=Keyboard([[Button('✅ Опубликовать', callback_data='study:publish')], [Button('Отмена', callback_data='study:cancel')]]))
    return CONFIRM


async def publish(update, context):
    await update.callback_query.answer()
    user = await user_for(update, context)
    draft = context.user_data.get('study_draft')
    if not user or not draft or (draft['kind'] == 'homework' and not user['is_admin']):
        await update.effective_message.reply_text('Публикация недоступна. Запусти создание заново.')
        return ConversationHandler.END
    if draft['kind'] == 'presentation' and (not draft.get('file_id') or
            not (draft.get('questions_text') or draft.get('questions_file_id'))):
        await update.effective_message.reply_text('Нужны файл презентации и вопросы. Начни создание заново: /cancel, затем /add_presentation.')
        return ConversationHandler.END
    try:
        item_id = await context.bot_data['AssignmentRepo'].create(draft, user)
    except DatabaseQueryError:
        logger.exception('Cannot publish assignment')
        await update.effective_message.reply_text('Не удалось сохранить. Проверь, что предмет и группа существуют, и попробуй ещё раз.')
        return CONFIRM
    context.user_data.pop('study_draft', None)
    await send(update, '✅ Опубликовано!', [[Button('Открыть', callback_data=f'study:view:{item_id}')]])
    return ConversationHandler.END


async def begin_question(update, context):
    await update.callback_query.answer()
    user = await user_for(update, context)
    if not user:
        return ConversationHandler.END
    item_id = int(update.callback_query.data.split(':')[2])
    item = await context.bot_data['AssignmentRepo'].get(item_id, user['group_id'], user['id'])
    if not item or item['kind'] != 'presentation' or not (user['is_admin'] or item['author_id'] == user['id']):
        await update.effective_message.reply_text('Вопросы добавляет автор презентации или администратор.')
        return ConversationHandler.END
    context.user_data['study_question'] = {'item_id': item_id}
    await update.effective_message.reply_text('Напиши вопрос (до 1000 символов). Отмена: /cancel.')
    return QUESTION


async def question(update, context):
    value = update.effective_message.text.strip()
    if not 1 <= len(value) <= 1000:
        await update.effective_message.reply_text('Вопрос должен содержать от 1 до 1000 символов.')
        return QUESTION
    context.user_data['study_question']['question'] = value
    await update.effective_message.reply_text('Теперь напиши подготовленный ответ (до 2500 символов).')
    return ANSWER


async def answer(update, context):
    value = update.effective_message.text.strip()
    if not 1 <= len(value) <= 2500:
        await update.effective_message.reply_text('Ответ должен содержать от 1 до 2500 символов.')
        return ANSWER
    user = await user_for(update, context)
    draft = context.user_data['study_question']
    repo = context.bot_data['AssignmentRepo']
    item = await repo.get(draft['item_id'], user['group_id'], user['id']) if user else None
    if not item or not (user['is_admin'] or item['author_id'] == user['id']):
        await update.effective_message.reply_text('Презентация больше недоступна.')
        return ConversationHandler.END
    try:
        await repo.add_question(item['id'], draft['question'], value)
    except DatabaseQueryError:
        logger.exception('Cannot save presentation question')
        await update.effective_message.reply_text('Не удалось сохранить ответ. Попробуй ещё раз.')
        return ANSWER
    context.user_data.pop('study_question', None)
    await update.effective_message.reply_text('✅ Вопрос и ответ добавлены.', reply_markup=Keyboard([[Button('К презентации', callback_data=f"study:view:{item['id']}")]]))
    return ConversationHandler.END


async def cancel(update, context):
    if update.callback_query:
        await update.callback_query.answer()
    context.user_data.pop('study_draft', None)
    context.user_data.pop('study_question', None)
    await update.effective_message.reply_text('Действие отменено.', reply_markup=Keyboard([[Button('Главное меню', callback_data='queue_back')]]))
    return ConversationHandler.END


def conversation_handler():
    text = filters.TEXT & ~filters.COMMAND
    return ConversationHandler(
        entry_points=[CommandHandler('add_homework', begin), CommandHandler('add_presentation', begin),
                      CallbackQueryHandler(begin, pattern=r'^study:new:(homework|presentation)$'),
                      CallbackQueryHandler(begin_question, pattern=r'^study:question:\d+$')],
        states={COURSE: [CallbackQueryHandler(choose_course, pattern=r'^study:course:\d+$')],
                TITLE: [MessageHandler(text, title)], DESCRIPTION: [MessageHandler(text, description)],
                DEADLINE: [CallbackQueryHandler(deadline_callback, pattern=r'^study:date:'), CommandHandler('skip', deadline), MessageHandler(text, deadline)],
                FILE: [CommandHandler('skip', attachment), MessageHandler(filters.Document.ALL | filters.PHOTO, attachment)],
                PRESENTATION_QUESTIONS: [MessageHandler(text | filters.Document.ALL, presentation_questions)],
                CONFIRM: [CallbackQueryHandler(publish, pattern=r'^study:publish$'), CallbackQueryHandler(cancel, pattern=r'^study:cancel$')],
                QUESTION: [MessageHandler(text, question)], ANSWER: [MessageHandler(text, answer)]},
        fallbacks=[CommandHandler('cancel', cancel), CommandHandler('start', cancel)],
    )
