
CREATE USER bot_tg WITH PASSWORD NULL; -- Это временная мера, с отсутствием пароля

--Здесь в будущем появятся создание полноценных таблиц


-- У бота есть права на существующие таблицы
GRANT CONNECT ON DATABASE botdb TO bot_tg;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO bot_tg;
