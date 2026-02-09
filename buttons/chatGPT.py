from telegram import Update          
from telegram.ext import ContextTypes

async def activateChatGPT(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Вызов метода chatGPT")
	
    await context.bot.send_message(
		chat_id=update.effective_chat.id,
		text=(
			"ЗАГЛУШКА !\n"
			"Напишите бота сами\n"
		)
	)

