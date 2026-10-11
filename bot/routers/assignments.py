from database import DataBase


class AssignmentRepo:
    def __init__(self, db: DataBase):
        self.db = db

    async def list(self, group_id, kind):
        return await self.db.fetchall(
            """SELECT a.*, c.title AS course_title FROM assignments a
               JOIN courses c ON c.id = a.course_id
               WHERE a.group_id = $1 AND a.kind = $2
               ORDER BY a.deadline ASC NULLS LAST, a.id DESC""", group_id, kind)

    async def get(self, item_id, group_id, user_id):
        return await self.db.fetchrow(
            """SELECT a.*, c.title AS course_title, u.username AS author_username, u.nicname AS author_nickname,
               EXISTS (SELECT 1 FROM assignment_progress p
                       WHERE p.assignment_id = a.id AND p.user_id = $3) AS completed
               FROM assignments a JOIN courses c ON c.id = a.course_id
               LEFT JOIN "user" u ON u.id = a.author_id
               WHERE a.id = $1 AND a.group_id = $2""", item_id, group_id, user_id)

    async def create(self, draft, user):
        return await self.db.fetchval(
            """INSERT INTO assignments
               (course_id, group_id, author_id, kind, title, description, deadline, file_id, file_type, questions_text, questions_file_id)
               VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11) RETURNING id""",
            draft['course_id'], user['group_id'], user['id'], draft['kind'],
            draft['title'], draft['description'], draft['deadline'], draft.get('file_id'),
            draft.get('file_type', 'document'), draft.get('questions_text'), draft.get('questions_file_id'))

    async def complete(self, item_id, user_id, completed):
        if completed:
            await self.db.execute(
                "INSERT INTO assignment_progress (assignment_id, user_id) VALUES ($1,$2) ON CONFLICT DO NOTHING",
                item_id, user_id)
        else:
            await self.db.execute(
                "DELETE FROM assignment_progress WHERE assignment_id=$1 AND user_id=$2", item_id, user_id)

    async def questions(self, item_id):
        return await self.db.fetchall(
            "SELECT * FROM presentation_questions WHERE assignment_id=$1 ORDER BY id", item_id)

    async def add_question(self, item_id, question, answer):
        await self.db.execute(
            "INSERT INTO presentation_questions (assignment_id, question, answer) VALUES ($1,$2,$3)",
            item_id, question, answer)

    async def delete(self, item_id):
        await self.db.execute("DELETE FROM assignments WHERE id=$1", item_id)

    async def update_presentation(self, item_id, user_id, draft, field):
        if field == 'file':
            return await self.db.fetchval(
                """UPDATE assignments SET file_id=$3, file_type='document'
                   WHERE id=$1 AND author_id=$2 AND kind='presentation' RETURNING id""",
                item_id, user_id, draft.get('file_id'))
        if field == 'questions':
            return await self.db.fetchval(
                """WITH updated AS (
                   UPDATE assignments SET questions_text=$3, questions_file_id=$4
                   WHERE id=$1 AND author_id=$2 AND kind='presentation' RETURNING id
                   ), removed AS (
                   DELETE FROM presentation_questions WHERE assignment_id IN (SELECT id FROM updated)
                   ) SELECT id FROM updated""", item_id, user_id,
                draft.get('questions_text'), draft.get('questions_file_id'))
        if field == 'details':
            return await self.db.fetchval(
                """UPDATE assignments SET title=$3, description=$4, deadline=$5
                   WHERE id=$1 AND author_id=$2 AND kind='presentation' RETURNING id""",
                item_id, user_id, draft['title'], draft['description'], draft['deadline'])
        raise ValueError('Unknown presentation field')
