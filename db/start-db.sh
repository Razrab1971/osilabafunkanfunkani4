#!/bin/bash

set -e

# Флаг инициализации
INIT_FLAG="/var/lib/postgresql/data/PG_VERSION"
PG_PID=""


if [ ! -f "$INIT_FLAG" ]; then
    echo "🔵 ПЕРВЫЙ ЗАПУСК - выполняем инициализацию"
	
	docker-entrypoint.sh postgres &
	PG_PID=$!
	
	until pg_isready -U postgres; do sleep 5; done
    
    DB_PASSWORDMY2=$(< /run/secrets/db-password2)
    if psql -U postgres -d botdb -c "CREATE USER bot_tg WITH PASSWORD '${DB_PASSWORDMY2}';"; then
        echo "Добвален пользователь"
    fi


	if psql -U postgres -d botdb -f start.sql; then
		echo "Запуск успешный"
	else
		echo "Ошибка захода"
	fi

else

	docker-entrypoint.sh postgres &
	PG_PID=$!

	echo "🍺 Штатный запуск"

fi

wait $PG_PID
