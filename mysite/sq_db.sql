CREATE TABLE IF NOT EXISTS posts (
id integer PRIMARY KEY AUTOINCREMENT,
title text NOT NULL,
text text NOT NULL,
url text NOT NULL,
time integer NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
id integer PRIMARY KEY AUTOINCREMENT,
name text NOT NULL,
email text NOT NULL,
psw text NOT NULL,
avatar BLOB DEFAULT NULL,
is_active integer DEFAULT 0,
time integer NOT NULL
);

CREATE TABLE IF NOT EXISTS comments (
id integer PRIMARY KEY AUTOINCREMENT,
user_id integer NOT NULL,
post_id integer NOT NULL,
text text NOT NULL,
time integer NOT NULL,
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS resume (
id integer PRIMARY KEY AUTOINCREMENT,
text text NOT NULL,
time integer NOT NULL
);

CREATE TABLE IF NOT EXISTS feedback (
id integer PRIMARY KEY AUTOINCREMENT,
user_id integer NOT NULL,
text text NOT NULL,
time integer NOT NULL,
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);