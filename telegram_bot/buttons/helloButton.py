from telegram import Update
from telegram.ext import ContextTypes

from authenticate_db import *

import logging

async def helloButton(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Вызов метода helloButton")
    

    logging.info(
    f"Вывод helloButton от имени: {
      await get_username(get_main_db(), get_user_id(update))
    }" 
    
    
    
    )
    # 1. Получаем объект пользователя
    user = update.effective_user
    
    # 2. Вытаскиваем конкретные данные
    user_id = user.id              # Числовой ID (типа 12345678)
    #first_name = user.first_name    # Имя
    #last_name = user.last_name      # Фамилия (может быть None)
    username = user.username        # Юзернейм без @ (может быть None)

    get_user_id(update)

    # Пример использования f-строки для ответа
    await context.bot.send_message(
		chat_id=update.effective_chat.id,
		text=(
        f"Ну, здравствуй:\n"
        f"{user.first_name} { user.last_name if user.last_name else "" }\n"
        f"Твой ID: {user_id}\n"
        f"{ f"Юзернейм: @ {username}" if username else 'Где Юзернейм ?'}"
		)
	)	





async def buttonInfoBot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Вызов метода buttonInfoBot")
	
    await context.bot.send_message(
		chat_id=update.effective_chat.id,
		text=(
		f"Этот бот создан студентами кафедры ФН11.\n"
		f"Предназначен для удобного взаимодействия с несколькими нейросетями.\n"
		)
	)

