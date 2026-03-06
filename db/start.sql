CREATE USER bot_tg WITH PASSWORD '1234vushelzaiqyugulat'; -- Это временная мера, с отсутствием пароля

--Здесь в будущем появятся создание полноценных таблиц

CREATE TABLE type_user(
	text TEXT PRIMARY KEY
);

CREATE TABLE users(
	id TEXT PRIMARY KEY,
	name CHAR(21),
	type_user TEXT REFERENCES type_user(text),
	first_connect DATE NOT NULL 
);


CREATE TABLE IF NOT EXISTS user_llm_settings (
    user_id TEXT PRIMARY KEY REFERENCES users(id),
    provider TEXT NOT NULL DEFAULT 'stub',
    model TEXT NOT NULL DEFAULT 'default',
    temperature REAL NOT NULL DEFAULT 0.7
);

-- Ограничения на таблицы 

CREATE OR REPLACE FUNCTION prevent_column_update()
RETURNS TRIGGER AS $$
BEGIN
	IF OLD.first_connect IS DISTINCT FROM NEW.first_connect THEN
		RAISE EXCEPTION 'Изменять время первого подключения запрещено';
	END IF;
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER present_users_first_connect
	BEFORE UPDATE ON users
	FOR EACH ROW
	EXECUTE FUNCTION prevent_column_update();

-- Заполнение таблиц

INSERT INTO type_user(text) VALUES
('Разработчик'),
('Пользователь'),
('Забанен');


INSERT INTO users(id, type_user, first_connect) VALUES
('0245498286 ', 'Разработчик', '2026-01-13'),
('580992405 ', 'Разработчик', '2026-01-13'),
('6811315631 ', 'Разработчик', '2026-01-13');

-- У бота есть права на существующие таблицы
GRANT CONNECT ON DATABASE botdb TO bot_tg;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE users TO bot_tg;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE user_llm_settings TO bot_tg;
