import logging

from typing import Dict
import re
from threading import Lock

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler 

import view

from authenticate_db import get_main_db, get_user_id, check_user_no_pro 


class Programm:
	razrab_activate: Dict[str, Dict[str, any]] = {}
	_lock = Lock()  # синхронизация потоков

	@classmethod
	def set(cls, user_id: str, key: str, value: any):
		with cls._lock: 
			if user_id not in cls.razrab_activate:
				cls.razrab_activate[user_id] = {}
				cls.razrab_activate[user_id][key] = value

	@classmethod
	def get(cls, user_id: str, key: str) -> any:
		with cls._lock:
			return cls.razrab_activate.get(user_id, {}).get(key, False)

	@classmethod
	def check(cls, user_id: str, key: str) -> bool:
		with cls._lock:
			return key in cls.razrab_activate.get(user_id, {})

	@classmethod
	def delete(cls, user_id: str, key: str):
		with cls._lock:
			if user_id in cls.razrab_activate and key in cls.razrab_activate[user_id]:
				del cls.razrab_activate[user_id][key]



async def commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
	if await check_user_no_pro( get_main_db(), update):
		return;

	await context.bot.send_message(
		chat_id=update.effective_chat.id,
		text=f"Меню разработчика",
		reply_markup=view.create_bot_menu_commands_razrab()
	);



# Исключения из правила для добавления кнопок
# они не в папке buttons, а именно здесь

class TelegramUserBotHandler(logging.Handler):
	def __init__(self, update, context):
		super().__init__();
		self.update = update
		self.context = context
		self.ignore_pattern = re.compile(r'HTTP Request|HTTP Response|api\.telegram\.org')

	def emit(self, record):
		msg = record.getMessage()
		if self.ignore_pattern.search(msg):
			return;


		message = f"{record.levelname}: {msg}"

		self.context.application.create_task(
			self.context.bot.send_message(
				chat_id=self.update.effective_chat.id,
				text=message
			)
		)
		

#Включение логов
async def start_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
	user_id = get_user_id(update);
	if Programm.check(user_id, "handler_log"):
		return;
	
	
	handler = TelegramUserBotHandler(update, context)
	handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

	logging.getLogger().addHandler(handler)

	Programm.set(user_id, "handler_log", handler) 

	await context.bot.send_message(
		chat_id=update.effective_chat.id,
		text=f"Логирование перенаправлено в чат"
	)



#Выключение логов
async def end_log(update: Update, context: ContextTypes.DEFAULT_TYPE):
	user_id = get_user_id(update)
	if await check_user_no_pro( get_main_db(), update):
		return;

	handler = Programm.get(user_id, "handler_log")
	if handler is not None:
		logging.getLogger().removeHandler(handler)
		
	
	Programm.delete(user_id, "handler_log")
	await context.bot.send_message(
		chat_id=update.effective_chat.id,
		text=f"Логирование перенаправлено в logging"
	)

#Возвращает список пользователей
async def list_users(update: Update, context=ContextTypes.DEFAULT_TYPE):
	try:
		db = get_main_db()
		record = await db.fetch("SELECT COUNT(*) FROM users;")

		await context.bot.send_message(
			chat_id=update.effective_chat.id,
			text=f"Общее число пользователей: {record[0][0]}"
		)
	
	except Exception as e:
		logging.info(f"Ошибка при попытке получить пользователей: {e}")



async def button_commands_handler(update: Update, context=ContextTypes.DEFAULT_TYPE):
	logging.info("🚨 ХЕНДЛЕР РАЗРАБОТЧИКА ВЫЗВАН!")  
	query = update.callback_query  # Получаем данные о нажатии
	await query.answer()           # Убираем "часики" на кнопке в ТГ

	data = query.data
	match data:
		case "commands:start_logs":
			await start_logs(update, context)
		case "commands:list_users":
			await list_users(update, context);


async def command_list(update: Update, context=ContextTypes.DEFAULT_TYPE):
	await update.message.reply_text(
	#chat_id=update.effective_chat.id,
	text=(
		f"/clist - вызывает эту справку\n"
		f"\n"
		f"\n"
		f"/setname - меняет имя в БД\n"
		f"/command - панель разработчика\n"
		f"/elog - выключает Логирование\n"
		f"\n"
	))




def get_commands_func(app) -> None:
	start_handler = CommandHandler('command', commands)
	end_logs_handler = CommandHandler('elog', end_log)
	command_list_handler = CommandHandler('clist', command_list)

	buttons_handler = CallbackQueryHandler(button_commands_handler, pattern="^commands")

	app.add_handler(start_handler, group=1)
	app.add_handler(command_list_handler, group=1)
	app.add_handler(end_logs_handler, group=1)
	app.add_handler(buttons_handler, group=1)

