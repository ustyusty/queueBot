
-- ----------------------------
-- Очистка старых таблиц
-- ----------------------------

DROP TABLE IF EXISTS list_queue CASCADE;
DROP TABLE IF EXISTS "user" CASCADE;
DROP TABLE IF EXISTS "group" CASCADE;
DROP TABLE IF EXISTS pack CASCADE;
DROP TABLE IF EXISTS courses CASCADE;


CREATE TABLE "group" (
    id SERIAL PRIMARY KEY,
    title TEXT UNIQUE
);

-- ----------------------------
-- Таблица: courses
-- ----------------------------

CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    title TEXT UNIQUE
    );

-- ----------------------------
-- Таблица: user
-- ----------------------------

CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    tg_id BIGINT UNIQUE,
    group_id INTEGER REFERENCES "group"(id) ON DELETE SET NULL,
    firstname VARCHAR(255),
    surname VARCHAR(255),
    put_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------
-- Таблица: pack
-- ----------------------------

CREATE TABLE pack (
    id SERIAL PRIMARY KEY,
    courses_id INTEGER REFERENCES courses(id) ON DELETE SET NULL,
    title VARCHAR(255),
    questions TEXT,
    deadline DATE
);

-- ----------------------------
-- Таблица: list_queue
-- ----------------------------

CREATE TABLE list_queue (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE,
    pack_id INTEGER REFERENCES pack(id) ON DELETE CASCADE,
    priority_queue INTEGER,
    is_pass BOOLEAN DEFAULT FALSE,
    put_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);