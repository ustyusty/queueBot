import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock
from datetime import date
from bot.services.deadline import month_keyboard

from bot.handlers import assignments as handlers
from bot.handlers import register_handler
from telegram.ext import Application


class AssignmentFlows(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.user = {'id': 7, 'group_id': 3, 'is_admin': False}
        self.repo = SimpleNamespace(get=AsyncMock(), create=AsyncMock(return_value=11),
                                    delete=AsyncMock(), complete=AsyncMock(), add_question=AsyncMock(),
                                    questions=AsyncMock(return_value=[]), update_presentation=AsyncMock(return_value=11))
        self.message = SimpleNamespace(reply_text=AsyncMock(), reply_photo=AsyncMock(),
            reply_document=AsyncMock(), text='', document=None, photo=[])
        self.query = SimpleNamespace(answer=AsyncMock(), edit_message_text=AsyncMock(),
            edit_message_caption=AsyncMock(), edit_message_reply_markup=AsyncMock(), data='')
        self.update = SimpleNamespace(effective_user=SimpleNamespace(id=100),
                                      effective_message=self.message, callback_query=self.query)
        self.context = SimpleNamespace(bot_data={
            'UserRepo': SimpleNamespace(get_user=AsyncMock(return_value=self.user)),
            'AssignmentRepo': self.repo,
            'CourseRepo': SimpleNamespace(get_courses=AsyncMock(return_value=[{'id': 1, 'title': 'Предмет'}]))}, user_data={})

    async def test_homework_creation_requires_admin(self):
        self.query.data = 'study:new:homework'
        self.assertEqual(await handlers.begin(self.update, self.context), -1)
        self.assertNotIn('study_draft', self.context.user_data)

    async def test_photo_attachment_keeps_largest_photo(self):
        self.message.photo = [SimpleNamespace(file_id='small'), SimpleNamespace(file_id='large')]
        self.context.user_data['study_draft'] = {'kind': 'homework', 'title': 'Задание', 'description': 'Текст', 'deadline': None}
        await handlers.attachment(self.update, self.context)
        self.assertEqual(self.context.user_data['study_draft']['file_id'], 'large')
        self.assertEqual(self.context.user_data['study_draft']['file_type'], 'photo')

    async def test_photo_sent_with_homework_caption(self):
        await handlers.send(self.update, 'Домашка', file_id='photo-id', file_type='photo')
        self.message.reply_photo.assert_awaited_once_with('photo-id', caption='Домашка', reply_markup=None)
        self.message.reply_document.assert_not_awaited()

    async def test_document_sent_with_homework_caption(self):
        await handlers.send(self.update, 'Домашка', file_id='doc-id')
        self.message.reply_document.assert_awaited_once_with('doc-id', caption='Домашка', reply_markup=None)

    async def test_long_caption_keeps_full_text(self):
        text = '😀' * 600
        await handlers.send(self.update, text, file_id='photo-id', file_type='photo')
        self.message.reply_photo.assert_awaited_once_with('photo-id', caption=None, reply_markup=None)
        self.message.reply_text.assert_awaited_once_with(text, reply_markup=None)

    async def test_completion_edits_existing_photo_caption(self):
        self.message.photo = [SimpleNamespace(file_id='photo-id')]
        await handlers.send(self.update, '✅ Выполнено', file_id='photo-id', file_type='photo')
        self.query.edit_message_caption.assert_awaited_once_with(caption='✅ Выполнено', reply_markup=None)
        self.message.reply_photo.assert_not_awaited()

    async def test_back_from_photo_sends_text_menu(self):
        self.message.photo = [SimpleNamespace(file_id='photo-id')]
        await handlers.send(self.update, 'Список домашек')
        self.message.reply_text.assert_awaited_once_with('Список домашек', reply_markup=None)
        self.query.edit_message_text.assert_not_awaited()

    async def test_author_only_deletion(self):
        self.query.data = 'study:remove:11'
        self.repo.get.return_value = {'id': 11, 'author_id': 8, 'kind': 'presentation'}
        await handlers.callback(self.update, self.context)
        self.repo.delete.assert_not_awaited()
        self.repo.get.assert_awaited_once_with(11, 3, 7)

    async def test_inaccessible_item_cannot_be_completed(self):
        self.query.data = 'study:done:11'
        self.repo.get.return_value = None
        await handlers.callback(self.update, self.context)
        self.repo.complete.assert_not_awaited()

    async def test_publish_rechecks_admin_rights(self):
        self.context.user_data['study_draft'] = {'kind': 'homework'}
        self.assertEqual(await handlers.publish(self.update, self.context), -1)
        self.repo.create.assert_not_awaited()

    async def test_presentation_publish(self):
        draft = {'kind': 'presentation', 'title': 'Тема', 'description': 'Описание',
                 'course_id': 1, 'deadline': None, 'file_id': 'presentation', 'questions_text': 'Почему?'}
        self.context.user_data['study_draft'] = draft
        self.assertEqual(await handlers.publish(self.update, self.context), -1)
        self.repo.create.assert_awaited_once_with(draft, self.user)
        self.assertNotIn('study_draft', self.context.user_data)

    async def test_presentation_file_is_optional(self):
        self.context.user_data['study_draft'] = {'kind': 'presentation'}
        self.message.text = '/skip'
        self.assertEqual(await handlers.attachment(self.update, self.context), handlers.PRESENTATION_QUESTIONS)
        self.assertIsNone(self.context.user_data['study_draft']['file_id'])

    async def test_presentation_without_file_can_be_published(self):
        draft = {'kind': 'presentation', 'questions_text': 'Почему?', 'file_id': None}
        self.context.user_data['study_draft'] = draft
        self.assertEqual(await handlers.publish(self.update, self.context), -1)
        self.repo.create.assert_awaited_once_with(draft, self.user)

    async def test_admin_cannot_add_someone_elses_questions(self):
        self.user['is_admin'] = True
        self.repo.get.return_value = {'id': 11, 'kind': 'presentation', 'author_id': 8}
        self.query.data = 'study:question:11'
        self.assertEqual(await handlers.begin_question(self.update, self.context), -1)
        self.assertNotIn('study_question', self.context.user_data)

    async def test_admin_cannot_edit_someone_elses_presentation(self):
        self.user['is_admin'] = True
        self.repo.get.return_value = {'id': 11, 'kind': 'presentation', 'author_id': 8}
        self.query.data = 'study:edit:questions:11'
        self.assertEqual(await handlers.begin_edit(self.update, self.context), -1)
        self.assertNotIn('study_draft', self.context.user_data)

    async def test_edit_uses_update_instead_of_new_record(self):
        draft = {'id': 11, 'kind': 'presentation', 'edit_field': 'file', 'file_id': 'new-file'}
        self.context.user_data['study_draft'] = draft
        await handlers.publish(self.update, self.context)
        self.repo.update_presentation.assert_awaited_once_with(11, 7, draft, 'file')
        self.repo.create.assert_not_awaited()

    async def test_card_includes_speaker_questions_and_file(self):
        item = {'id': 11, 'kind': 'presentation', 'course_title': 'Предмет', 'title': 'Тема',
                'description': 'Описание', 'deadline': None, 'author_id': 7,
                'author_username': 'speaker', 'author_nickname': 'Имя',
                'questions_text': 'Почему?', 'questions_file_id': None, 'file_id': 'slides'}
        await handlers.show_item(self.update, self.context, item)
        self.message.reply_document.assert_awaited_once()
        caption = self.message.reply_document.call_args.kwargs['caption']
        self.assertIn('@speaker', caption)
        self.assertIn('Почему?', caption)
        self.assertNotIn('Подготовленных вопросов: 0', caption)

    async def test_card_falls_back_to_nickname_and_attaches_both_files(self):
        item = {'id': 11, 'kind': 'presentation', 'course_title': 'Предмет', 'title': 'Тема',
                'description': 'Описание', 'deadline': None, 'author_id': 8,
                'author_username': None, 'author_nickname': 'Докладчик',
                'questions_text': None, 'questions_file_id': 'questions', 'file_id': 'slides'}
        await handlers.show_item(self.update, self.context, item)
        self.assertEqual(self.message.reply_document.await_count, 2)
        text = self.query.edit_message_text.call_args.args[0]
        self.assertIn('Докладчик: Докладчик', text)
        buttons = self.query.edit_message_text.call_args.kwargs['reply_markup'].inline_keyboard
        self.assertFalse(any('edit:' in b.callback_data or 'question:' in b.callback_data for row in buttons for b in row))

    async def test_presentation_file_followed_by_questions(self):
        self.context.user_data['study_draft'] = {'kind': 'presentation'}
        self.message.document = SimpleNamespace(file_id='slides')
        self.assertEqual(await handlers.attachment(self.update, self.context), handlers.PRESENTATION_QUESTIONS)
        self.assertEqual(self.context.user_data['study_draft']['file_id'], 'slides')

    async def test_questions_text_and_document(self):
        draft = {'kind': 'presentation', 'title': 'Тема', 'description': 'Описание', 'deadline': None, 'file_id': 'slides'}
        self.context.user_data['study_draft'] = draft
        self.message.text = '1. Почему?\nОтвет: потому что.'
        self.assertEqual(await handlers.presentation_questions(self.update, self.context), handlers.CONFIRM)
        self.assertEqual(draft['questions_text'], self.message.text)
        self.message.document = SimpleNamespace(file_id='questions-doc')
        await handlers.presentation_questions(self.update, self.context)
        self.assertEqual(draft['questions_file_id'], 'questions-doc')
        self.assertIsNone(draft['questions_text'])

    async def test_calendar_date_then_time(self):
        self.context.user_data['study_draft'] = {'kind': 'homework'}
        self.query.data = 'study:date:day:2028-02-29'
        self.assertEqual(await handlers.deadline_callback(self.update, self.context), handlers.DEADLINE)
        self.query.data = 'study:date:time:23:59'
        self.assertEqual(await handlers.deadline_callback(self.update, self.context), handlers.FILE)
        selected = self.context.user_data['study_draft']['deadline']
        self.assertEqual(selected.date(), date(2028, 2, 29))
        self.assertEqual((selected.hour, selected.minute), (23, 59))
        self.assertEqual(selected.utcoffset().total_seconds(), 7 * 3600)

    async def test_no_deadline_button(self):
        self.context.user_data['study_draft'] = {'kind': 'homework'}
        self.query.data = 'study:date:none'
        self.assertEqual(await handlers.deadline_callback(self.update, self.context), handlers.FILE)
        self.assertIsNone(self.context.user_data['study_draft']['deadline'])

    async def test_invalid_deadline_and_local_timezone(self):
        self.context.user_data['study_draft'] = {}
        self.message.text = '31.02.2026 12:00'
        self.assertEqual(await handlers.deadline(self.update, self.context), handlers.DEADLINE)
        self.message.text = '20.10.2026 23:59'
        self.assertEqual(await handlers.deadline(self.update, self.context), handlers.FILE)
        date = self.context.user_data['study_draft']['deadline']
        self.assertEqual(date.utcoffset().total_seconds(), 7 * 3600)

    async def test_question_save_rechecks_ownership(self):
        self.context.user_data['study_question'] = {'item_id': 11, 'question': 'Почему?'}
        self.message.text = 'Потому что'
        self.repo.get.return_value = {'id': 11, 'author_id': 8}
        self.assertEqual(await handlers.answer(self.update, self.context), -1)
        self.repo.add_question.assert_not_awaited()


class RegistrationTests(unittest.TestCase):
    def test_calendar_leap_day_and_year_navigation(self):
        callbacks = [b.callback_data for row in month_keyboard(2028, 2).inline_keyboard for b in row]
        self.assertIn('study:date:day:2028-02-29', callbacks)
        callbacks = [b.callback_data for row in month_keyboard(2026, 12).inline_keyboard for b in row]
        self.assertIn('study:date:month:2027:1', callbacks)

    def test_handlers_can_be_registered(self):
        app = Application.builder().token('123:TEST').build()
        register_handler(app)
        self.assertGreater(len(app.handlers[0]), 10)


if __name__ == '__main__':
    unittest.main()
