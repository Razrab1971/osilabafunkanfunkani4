from telegram import Update
from telegram.ext import ContextTypes

import view
from authenticate_db import get_user_id
from connect_ai.llm_settings import get_llm_settings
from connect_ai.llm_core import call_llm_text

LLM_MODE_KEY = "llm_chat_mode"

async def llm_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get(LLM_MODE_KEY):
        return

    text = (update.message.text or "").strip()

    if text == r"\exit":
        context.user_data[LLM_MODE_KEY] = False
        await update.message.reply_text("Ок, вышел в меню.", reply_markup=view.create_bot_menu())
        return

    user_id = get_user_id(update)
    settings = await get_llm_settings(user_id)
    answer = await call_llm_text(text, settings)
    await update.message.reply_text(answer, reply_markup=view.create_llm_chat_menu())