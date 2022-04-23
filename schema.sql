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
CREATE INDEX topic_id_index ON threads(topic_id);
CREATE INDEX user_id_index ON threads(user_id);
