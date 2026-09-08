from asyncpg import Record

from database import DataBase


class CourseRepo:
    """Database operations for courses."""

    def __init__(self, db: DataBase):
        self.db = db

    async def add_course(self, title: str) -> Record:
        course = await self.db.fetchrow(
            """
            INSERT INTO courses (title)
            VALUES ($1)
            ON CONFLICT (title) DO UPDATE SET title = EXCLUDED.title
            RETURNING id, title
            """,
            title,
        )
        if course is None:
            raise RuntimeError("Course was not created")
        return course

    async def get_course(self, course_id: int) -> Record | None:
        return await self.db.fetchrow(
            """
            SELECT id, title
            FROM courses
            WHERE id = $1
            """,
            course_id,
        )

    async def get_courses(self) -> list[Record]:
        return await self.db.fetchall(
            """
            SELECT id, title
            FROM courses
            ORDER BY title, id
            """
        )
