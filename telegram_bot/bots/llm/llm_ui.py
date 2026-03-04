from telegram import Update
from telegram.ext import ContextTypes

import view
from authenticate_db import get_user_id
from connect_ai.llm_settings import get_llm_settings, set_llm_model, set_llm_temperature, set_llm_provider
from connect_ai.settings import get_llm_settings, set_llm_model, set_llm_temperature, set_llm_provider

LLM_MODE_KEY = "llm_chat_mode"

async def activate_llm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = get_user_id(update)
    st = await get_llm_settings(user_id)

    if update.callback_query:
        await update.callback_query.edit_message_text(
            "Настройки LLM:",
            reply_markup=view.create_llm_settings_menu(st["provider"], st["model"], st["temperature"]),
        )
    else:
        await update.message.reply_text(
            "Настройки LLM:",
            reply_markup=view.create_llm_settings_menu(st["provider"], st["model"], st["temperature"]),
        )

async def llm_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    user_id = get_user_id(update)

    # === открыть экран настроек ===
    if data == "llm:settings":
        st = await get_llm_settings(user_id)
        await q.edit_message_text(
            "Настройки LLM:",
            reply_markup=view.create_llm_settings_menu(
                st["provider"], st["model"], st["temperature"]
            ),
        )
        return

    # === открыть выбор провайдера ===
    if data == "llm:open_provider":
        st = await get_llm_settings(user_id)
        await q.edit_message_text(
            "Выбери провайдера:",
            reply_markup=view.create_llm_provider_menu(st["provider"]),
        )
        return

    # === выбрать провайдера ===
    if data.startswith("llm:set_provider:"):
        provider = data.split(":", 2)[2]
        await set_llm_provider(user_id, provider)
        st = await get_llm_settings(user_id)
        await q.edit_message_text(
            f"Провайдер сохранён: {provider}\nНастройки LLM:",
            reply_markup=view.create_llm_settings_menu(
                st["provider"], st["model"], st["temperature"]
            ),
        )
        return

    # === открыть выбор моделей ===
    if data == "llm:open_models":
        await q.edit_message_text(
            "Выбери модель LLM:",
            reply_markup=view.create_llm_models_menu()
        )
        return

    # === выбрать модель ===
    if data.startswith("llm:set_model:"):
        model = data.split(":", 2)[2]
        await set_llm_model(user_id, model)
        st = await get_llm_settings(user_id)
        await q.edit_message_text(
            f"Модель сохранена: {model}\nНастройки LLM:",
            reply_markup=view.create_llm_settings_menu(
                st["provider"], st["model"], st["temperature"]
            ),
        )
        return

    # === открыть выбор температуры ===
    if data == "llm:open_temp":
        st = await get_llm_settings(user_id)
        await q.edit_message_text(
            "Выбери температуру:",
            reply_markup=view.create_llm_temperature_menu(st["temperature"]),
        )
        return

    # === выбрать температуру ===
    if data.startswith("llm:set_temp:"):
        val = float(data.split(":", 2)[2])
        await set_llm_temperature(user_id, val)
        st = await get_llm_settings(user_id)
        await q.edit_message_text(
            f"Температура сохранена: {val:.1f}\nНастройки LLM:",
            reply_markup=view.create_llm_settings_menu(
                st["provider"], st["model"], st["temperature"]
            ),
        )
        return

    # === вход в чат ===
    if data == "llm:enter_chat":
        context.user_data[LLM_MODE_KEY] = True
        st = await get_llm_settings(user_id)
        await q.edit_message_text(
            f"Чат LLM включён (provider={st['provider']}, model={st['model']}, temp={st['temperature']:.1f}).\n"
            f"Пиши сообщение. Для выхода: \\exit или кнопка ниже.",
            reply_markup=view.create_llm_chat_menu(),
        )
        return

    # === выход в главное меню ===
    if data == "llm:exit":
        context.user_data[LLM_MODE_KEY] = False
        await q.edit_message_text("Продолжим ?", reply_markup=view.create_bot_menu())
        return

