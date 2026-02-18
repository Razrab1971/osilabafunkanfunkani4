import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler 

from authenticate_db import init_db, get_main_db, get_user_id, registrate_user, check_user_ban


import view

# Для каждой отдельной логики бота
# Создавать свой файл с логикой функции по типу раздела {LLM, text2image, text2video, second2all}
from buttons.helloButton import helloButton, buttonInfoBot
from buttons.buttonsLLM import * 

from commands.authenticate import get_setname_user_handler, get_activate_user_handler_func
from commands.prog_command import get_commands_func



logging.basicConfig(
		format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
		level=logging.INFO
	)



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
	#Регистрация пользователя
	db = get_main_db()
	logging.info(
		f"Регистрация пользователя: {
			not await registrate_user(
				db,
				get_user_id(update),
				update.effective_user.first_name
			)
		}",
	)

	await update.message.reply_text(
			"Начнём ?",
			reply_markup=view.create_bot_menu()
		)


#Обработчик нажатий на кнопки
async def button_handler_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
	logging.info("🚨 ХЕНДЛЕР ВЫЗВАН!")  
	query = update.callback_query  # Получаем данные о нажатии
	await query.answer()           # Убираем "часики" на кнопке в ТГ

# Вытаскиваем ту самую "метку" (callback_data)
# Например, если нажали первую кнопку, data будет "action:text"
	data = query.data
	
	print("🔥 menu:llm ВЫЗВАН!")  # 👈 ЭТОГО НЕТ В ЛОГАХ!
	match data:
		case "menu:llm":
			logging.info("Кнопка LLM нажата")
		case "menu:text2image":
			pass
		case "menu:text2video":
			pass
		case "menu:second2all":
			pass
		case "menu:helloButton":
			await helloButton(update, context)
			await context.bot.send_message(
				chat_id=update.effective_chat.id,
				text="Продолжим ?",
				reply_markup=view.create_bot_menu()
			)
		case "menu:buttonInfoBot":
			await buttonInfoBot(update, context)

"""
	if data == "action:helloButton": # Обработка нажатии кнопки
	elif data == "action:activateChatGPT":
		await activateChatGPT(update, context)
"""




#Оставлю для тестов ботовотсва
TOKEN = '8342225271:AAG21KFoKOsJPl9fxvyHEDXkw8_LD8uZJ9A'




if __name__ == '__main__':
	application = ApplicationBuilder().token(TOKEN).build()
	init_db()

	start_handler = CommandHandler('start', start)
	auten_handler = get_setname_user_handler()
	
	get_activate_user_handler_func(application)
	get_commands_func(application)

	application.add_handler(start_handler, group=1)

	application.add_handler(auten_handler, group=1)
	application.add_handler(CallbackQueryHandler(button_handler_menu, pattern="^menu:"), group=1)

	print("Поехали")
	application.run_polling()
