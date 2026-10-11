BEGIN;
CREATE TABLE IF NOT EXISTS assignments (
    id SERIAL PRIMARY KEY,
    course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    group_id INTEGER NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
    author_id INTEGER REFERENCES "user"(id) ON DELETE SET NULL,
    kind TEXT NOT NULL CHECK (kind IN ('homework', 'presentation')),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    deadline TIMESTAMPTZ,
    file_id TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS presentation_questions (
    id SERIAL PRIMARY KEY,
    assignment_id INTEGER NOT NULL REFERENCES assignments(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    answer TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS assignment_progress (
    assignment_id INTEGER REFERENCES assignments(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE,
    completed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (assignment_id, user_id)
);
CREATE INDEX IF NOT EXISTS assignments_group_kind ON assignments (group_id, kind);
ALTER TABLE assignments ADD COLUMN IF NOT EXISTS file_type TEXT NOT NULL DEFAULT 'document'
    CHECK (file_type IN ('document', 'photo'));
ALTER TABLE assignments ADD COLUMN IF NOT EXISTS questions_text TEXT;
ALTER TABLE assignments ADD COLUMN IF NOT EXISTS questions_file_id TEXT;
COMMIT;
