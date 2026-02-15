from telegram import Update
from telegram.ext import ConversationHandler, CallbackQueryHandler, ContextTypes, CommandHandler, MessageHandler, ApplicationHandlerStop, filters

from authenticate_db import ManagerDB, get_user_id, set_name_user, get_main_db, check_user_ban 

import logging


SETNEWNAME = range(1)


async def what_is_you_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
	print('Вызов метода what_is_you_name')
	
	await context.bot.send_message(
			chat_id=update.effective_chat.id,
			text="Напишите как к Вам обращаться: "
	)
	return SETNEWNAME

async def set_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
	new_name = update.message.text
	
	result = await set_name_user(
		get_main_db(), 
		get_user_id(update),
		new_name
	)

	if result:	
		await context.bot.send_message(
				chat_id=update.effective_chat.id,
				text=(
					"Не удалось изменить имя\n"
					"Попробуйте ещё раз /setname"
				)
		)
	else:
		await context.bot.send_message(
				chat_id=update.effective_chat.id,
				text=f"Теперь Вы: {new_name}"
		)
		


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
	await context.bot.send_message(
			chat_id=update.effective_chat.id,
			text="Конец"
	)
	return ConversationHandler.END


def get_setname_user_handler() -> ConversationHandler:
	return ConversationHandler(
		entry_points=[CommandHandler('setname', what_is_you_name)],
		states={
			SETNEWNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_name)]
		},
		fallbacks=[CommandHandler('cancel', cancel)],
		allow_reentry=True
	)

# Банана

async def activate_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
	logging.info('СHECK user banana')
	if (await check_user_ban( 
		get_main_db(),
		update
	)):
		await context.bot.send_message(
			chat_id=update.effective_chat.id,
			text=(
				f"Поздравляю с получением Банана"
			)
		)
		raise ApplicationHandlerStop()
	

def get_activate_user_handler_func(app) -> None:
	message_handler = MessageHandler( filters = filters.ALL, callback=activate_user)
	button_handler = CallbackQueryHandler(activate_user)

	app.add_handler(message_handler, group=0)
	app.add_handler(button_handler,  group=0)

	
