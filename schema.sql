CREATE TABLE users(
	id SERIAL PRIMARY KEY,
	username TEXT UNIQUE NOT NULL,
	password_hash TEXT NOT NULL,
	is_admin BOOL DEFAULT FALSE
);

CREATE TABLE topics(
	id SERIAL PRIMARY KEY,
	topic TEXT UNIQUE NOT NULL,
	visible BOOL DEFAULT TRUE
);

CREATE TABLE threads(
	id SERIAL PRIMARY KEY,
	topic_id INTEGER NOT NULL,
	user_id INTEGER NOT NULL,
	subject TEXT NOT NULL,
	visible BOOL DEFAULT TRUE,
	CONSTRAINT fk_topic
		FOREIGN KEY(topic_id)
			REFERENCES topics(id),
	CONSTRAINT fk_user
		FOREIGN KEY(user_id)
			REFERENCES users(id)
);
CREATE INDEX thread_topic_id_index ON threads(topic_id);
CREATE INDEX thread_user_id_index ON threads(user_id);

CREATE TABLE messages(
	id SERIAL PRIMARY KEY,
	thread_id INTEGER NOT NULL,
	user_id INTEGER NOT NULL,
	message TEXT NOT NULL,
	time TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
	visible BOOL DEFAULT TRUE,
	CONSTRAINT fk_thread
		FOREIGN KEY(thread_id)
			REFERENCES threads(id),
	CONSTRAINT fk_user
		FOREIGN KEY(user_id)
			REFERENCES users(id)
);
CREATE INDEX message_thread_id_index ON messages(thread_id);
CREATE INDEX message_user_id_index ON messages(user_id);
