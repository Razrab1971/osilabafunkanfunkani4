import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, ContextTypes

import view

# Для каждой отдельной логики бота
# Создавать свой файл с логикой функции
from buttons.helloButton import helloButton
from buttons.chatGPT import activateChatGPT



logging.basicConfig(
		format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
		level=logging.INFO
	)



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
	await update.message.reply_text(
			"Начнём ?",
			reply_markup=view.create_bot_menu()
		)


#Обработчик нажатий на кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
	query = update.callback_query  # Получаем данные о нажатии
	await query.answer()           # Убираем "часики" на кнопке в ТГ

# Вытаскиваем ту самую "метку" (callback_data)
# Например, если нажали первую кнопку, data будет "action:text"
	data = query.data

	if data == "action:helloButton": # Обработка нажатии кнопки
		await helloButton(update, context)
		await context.bot.send_message(
				chat_id=update.effective_chat.id,
				text="Продолжим ?",
				reply_markup=view.create_bot_menu()
		)
	elif data == "action:activateChatGPT":
		await activateChatGPT(update, context)



#Оставлю для тестов ботовотсва
TOKEN = '8342225271:AAG21KFoKOsJPl9fxvyHEDXkw8_LD8uZJ9A'




if __name__ == '__main__':
	application = ApplicationBuilder().token(TOKEN).build()

	start_handler = CommandHandler('start', start)
	application.add_handler(start_handler)

	application.add_handler(CallbackQueryHandler(button_handler, pattern="^action:"))

	print("Поехали")
	application.run_polling()
