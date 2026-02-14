import asyncio
import asyncpg
import threading
import os
from typing import Dict, Optional


import subprocess
import logging


from telegram import Update 
from datetime import datetime, date


class ManagerDB:
	_instances: Dict[str, 'ManagerDB'] = {}
	_register_lock = threading.Lock()

	def __new__(cls, db_name: str, *args, **kwargs):
		with cls._register_lock:
			if db_name in cls._instances:
				return cls._instances[db_name]
	
			instance = super().__new__(cls)
			cls._instances[db_name] = instance
			return instance  



	def __init__(self, db_name: str, dsn: str):
		if not hasattr(self, 'initialized'):
			self.db_name = db_name
			self.dsn = dsn
			self.pool: Optional[asyncpg.Pool] = None
			self.initialized = True
			self.db_lock = asyncio.Lock()


	async def _self_connect(self):
		logging.info("Запуск async def connect")
		if self.pool is None:
			self.pool = await asyncpg.create_pool(
				dsn=self.dsn,
				min_size=5,
				max_size=20
			)
			print("Пул соединений успешно создан")

	async def connect(self):
		async with self.db_lock:
			await self._self_connect();


	async def fetch(self, query: str, *args):
		logging.info("Запуск async def fetch")
		if self.pool is None:
			async with self.db_lock:
				await self._self_connect()
		return await self.pool.fetch(query, *args)


	async def close(self):
		async with self.db_lock:
			if self.pool is not None:
				await self.pool.close()
				self.pool = None



# Вот это с настройками бд


def init_db() -> ManagerDB:
	return ManagerDB("aut-db", os.getenv('DB_DSN'))

def get_main_db()->ManagerDB:
	return ManagerDB("aut-db", "");



# Вот здесь полезные функции для работы с бд

# Принимает user.id и возвращает уже нормальный id для бд
def computer_user_id(user_id: str) -> str:
	return subprocess.run(
			['/app/shifr', str(user_id)],
			capture_output=True,
			text=True
		).stdout



# Возвращает уже нужный user.id
def get_user_id(update: Update) -> str:
	return computer_user_id(update.effective_user.id);

# Возвращает имя пользователя по id
def get_name_standart():
	return "Пользователь"

async def get_username(db: ManagerDB, user_id: str) -> str:
	records = await db.fetch("SELECT name FROM users WHERE id = $1", user_id);
	if records and records[0][0] is not None:
		return records[0][0]
	return get_name_standart()


# Регистария пользователя
# True - ошибка вставки
# False - успешная вставка
async def registrate_user(
	db: ManagerDB,
	user_id: str,
	name: str | None = None,
	type_user: str | None = None
) -> bool:

	first_connect = datetime.utcnow()
	
	try:

		records = await db.fetch(
			'INSERT INTO users(id, name, type_user, first_connect) VALUES ($1, $2, $3, $4)',
			user_id, name, (type_user if type_user is not None else get_name_standart() ), first_connect
		)
		
		return False;
	except Exception as e:
		logging.info(f"Ошибка при попытке вставки нового пользователя {e}")
		return True;

# Изменение имени в обращении к пользователю
async def set_name_user(
	db: ManagerDB,
	user_id: str,
	name: str
) -> bool:
	try:
		await db.fetch(
			'UPDATE users SET name = $2 WHERE id = $1',
			user_id, name
		)

		return False;
	except Exception as e:
		return True;



