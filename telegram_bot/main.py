import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from authenticate_db import init_db, get_main_db, get_user_id, registrate_user, check_user_ban
from bots.llm.llm_ui import activate_llm, llm_callback_handler
from bots.llm.llm_chat import llm_text_handler
from bots_bootstrap import register_all_bots
from registry import get_bot

import view

# Для каждой отдельной логики бота
# Создавать свой файл с логикой функции по типу раздела {LLM, text2image, text2video, second2all}
from buttons.helloButton import helloButton, buttonInfoBot
from buttons.buttonsLLM import *

from commands.authenticate import get_setname_user_handler, get_activate_user_handler_func
from commands.prog_command import get_commands_func

from script_bot.script_commands import general_script_cmd, script_run_cmd, sexit_cmd, on_document


logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = get_main_db()

    is_new = not await registrate_user(
        db,
        get_user_id(update),
        update.effective_user.first_name
    )
    logging.info(f"Регистрация пользователя: {is_new}")

    await update.message.reply_text(
        "Начнём ?",
        reply_markup=view.create_bot_menu()
    )

async def unknown_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Команда не распознана. Проверь /clist")

async def bot_activate_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data  # bot:activate:<bot_id>
    bot_id = data.split(":", 2)[2]
    spec = get_bot(bot_id)
    if not spec:
        await q.edit_message_text("Бот не найден. Обнови меню /start", reply_markup=view.create_bot_menu())
        return
    await spec.activate(update, context)


#Обработчик нажатий на кнопки
async def button_handler_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("🚨 ХЕНДЛЕР ВЫЗВАН!")
    query = update.callback_query  # Получаем данные о нажатии
    await query.answer()           # Убираем "часики" на кнопке в ТГ

# Вытаскиваем ту самую "метку" (callback_data)
# Например, если нажали первую кнопку, data будет "action:text"
    data = query.data
    logging.info(f"Callback data received: {data}")

    print("🔥 menu:llm ВЫЗВАН!")  # 👈 ЭТОГО НЕТ В ЛОГАХ!
    match data:
        case "menu:llm":
            await query.edit_message_text("Выбери LLM:", reply_markup=view.create_bot_menu_choice_llm())
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
    application.add_handler(CallbackQueryHandler(llm_callback_handler, pattern="^llm:"), group=1)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, llm_text_handler), group=1)
    application.add_handler(CallbackQueryHandler(bot_activate_handler, pattern="^bot:activate:"), group=1)
    application.add_handler(CommandHandler("general_script", general_script_cmd), group=1)
    application.add_handler(CommandHandler("script_run", script_run_cmd), group=1)
    application.add_handler(CommandHandler("sexit", sexit_cmd), group=1)
    application.add_handler(MessageHandler(filters.Document.ALL, on_document), group=1)
    application.add_handler(MessageHandler(filters.COMMAND, unknown_cmd), group=1)

    print("Поехали")
    register_all_bots()
    application.run_polling()
