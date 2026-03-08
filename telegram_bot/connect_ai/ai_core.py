import logging

from telegram import Update
from telegram.ext import ContextTypes

import view
import asyncio
import re

from authenticate_db import get_user_id
from connect_ai.llm_settings import get_llm_settings
from connect_ai.llm_core import call_llm_text
from connect_ai.model_ai_core import ModelAI, Provider_Type, Bytes_and_type, Data_Type



from g4f.client import Client



client = Client()   # Один за всех, хотя бы чтобы заработало
bad_guys = ["Puter", "PuterJS", "Liaobots", "OpenaiChat", "Gemini", "Bing"] # За компанию



INTERCEPTOR_MODE = "interceptor_mode"

# Обработчик всех событий при нажатий
async def interceptor_text_toAI_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    activate_model = context.user_data.get(INTERCEPTOR_MODE, None)
    if activate_model is None:
        return

    text = (update.message.text or "").strip()

    if text == r"\exit":
        context.user_data[INTERCEPTOR_MODE] = None
        await update.message.reply_text("Ок, вышел в меню.", reply_markup=view.create_bot_menu())
        return

    logging.info("Перехватываем текст для AI")
    
    
    try:
        result = await general_send_message_AI(
            activate_model, Bytes_and_type(text.encode('utf-8'), Data_Type.text)
        )


        if result.types == Data_Type.text:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=result.data.decode('utf-8')
            )
    except ValueError as e:
        logging.warning(f"Запрос к нейросети выкинул заглушку: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Попробуйте повторить запрос"
        )
    except Exception as e:
        logging.warning(f"Запрос к нейросети выкинул ошибку: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Попробуйте другую нейросеть"
        )
        





#Цензор
url_pattern = r'(https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9.-]+\.[a-z]{2,6}(/[^\s]*)?)' 
def sensor(text: str) -> str:
    textLow = text.lower()
    if "the model does not exist in" in textLow or "important notice" in textLow:
        raise ValueError("Повторите свой запрос")

    return re.sub(url_pattern, '(---РКН---)', text)





# Основная функция для обработки сообщений
async def general_send_message_AI(model: ModelAI, tuples: Bytes_and_type) -> Bytes_and_type:
    if model.provider == Provider_Type.G4f:
        return await _general_send_message_Provider_G4f(model, tuples)
    else:
        raise Exception('Неизвестный провайдер')

async def _general_send_message_Provider_G4f(model: ModelAI, tuples: Bytes_and_type) -> Bytes_and_type:
    response = await asyncio.to_thread(
        client.chat.completions.create,
        model=model.model,
        ignore_providers=bad_guys,
        messages=[{
            "role": "user",
            "content": tuples.data.decode('utf-8')
        }],
        timeout=15
    )
    
    # 2. УНИВЕРСАЛЬНЫЙ ПАРСЕР ОТВЕТА
    if isinstance(response, str):
        # Бывает у простых провайдеров
        content = response
    elif hasattr(response, 'choices') and response.choices:
        # Стандарт: берем ПЕРВЫЙ элемент списка choices
        choice = response.choices[0]
        # Проверяем, это объект .message или словарь ["message"]
        if hasattr(choice, 'message'):
            content = choice.message.content
        else:
            content = choice.get('message', {}).get('content')
    else:
        content = None



    if content is None:
        raise Exception("Тишина в ответ")
    
    content = sensor(content)
    return Bytes_and_type(content.encode('utf-8'), Data_Type.text)

#import g4f
#def _general_send_message_Provider_G4f(model: ModelAI, tuples: Bytes_and_type) -> Bytes_and_type:
#    models_list = list(g4f.models.ModelUtils.convert.keys())
#    
#    query = tuples.data.decode('utf-8')
#
#    for text in models_list:
#        try:
#            response = client.chat.completions.create(
#                model=text,
#                ignore_providers=bad_guys,
#                messages=[{"role": "user", "content": query}],
#                timeout=20
#            )
#
#            content = None
#            # 1. Если это просто строка
#            if isinstance(response, str):
#                content = response
#            # 2. Если это объект с choices (наш случай с ошибкой)
#            elif hasattr(response, 'choices'):
#                # Берем первый элемент списка choices через индекс [0]
#                choice = response.choices[0]
#                # Проверяем, это объект с .message или словарь
#                if hasattr(choice, 'message'):
#                    content = choice.message.content
#                else:
#                    content = choice.get('message', {}).get('content')
#            # 3. Если это просто список (бывает и такое)
#            elif isinstance(response, list) and len(response) > 0:
#                content = response[0].get('content')
#
#            if content and len(str(content)) > 5:
#                logging.info(f"✅ У модели есть потенциал: {text}")
#            
#        except Exception as e:
#            logging.info(f"❌ Модель {text} мимо: {str(e)[:50]}")
#            continue
#
#    raise Exception("🤖 Все модели из списка промолчали")
