CREATE TABLE groups (
    id SERIAL PRIMARY KEY,
    title TEXT UNIQUE NOT NULL
);

CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    title TEXT UNIQUE NOT NULL
);

CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    tg_id BIGINT UNIQUE,
    group_id INTEGER REFERENCES groups(id) ON DELETE SET NULL,
    nicname VARCHAR(255),
    username VARCHAR(255),
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    register_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE list_queue (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE,
    course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
    is_pass BOOLEAN DEFAULT FALSE,
    register_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    close_at TIMESTAMP DEFAULT NULL
);

CREATE UNIQUE INDEX unique_active_queue_entry
    ON list_queue (user_id, course_id)
    WHERE is_pass = FALSE AND close_at IS NULL;
