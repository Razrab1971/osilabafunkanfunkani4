#!/bin/bash

set -e

# Флаг инициализации
INIT_FLAG="/var/lib/postgresql/data/.init_done"

docker-entrypoint.sh postgres &
PG_PID=$!


until pg_isready -U postgres; do sleep 1; done


if [ ! -f "$INIT_FLAG" ]; then
    echo "🔵 ПЕРВЫЙ ЗАПУСК - выполняем инициализацию"
	
	if psql -U postgres -d botdb -f start.sql; then
		echo "Запуск успешный"
	else
		echo "Ошибка захода"
	fi

else
	echo "🍺 Штатный запуск"

fi

wait $PG_PID
