from typing import Union, List
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

#Создание меню
"""
	buttons - массив кнопок
	n_cols - кол-во кнопок в колонке
	header_buttons - верхняя кнопка
	footer_buttons - нижняя кнопка
"""

def menu_build(
	buttons: List[InlineKeyboardButton],
	n_cols: int,
    header_buttons: Union[InlineKeyboardButton, List[InlineKeyboardButton]]=None,
    footer_buttons: Union[InlineKeyboardButton, List[InlineKeyboardButton]]=None
)->List[List[InlineKeyboardButton]]:
	menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
	if header_buttons:
		menu.insert(0, header_buttons if isinstance(header_buttons, list) else [header_buttons] )
	if footer_buttons:
		menu.append(footer_buttons if isinstance(footer_buttons, list) else [footer_buttons] )
	return menu



#Функция для выбора типа бота
def create_bot_menu():
	return InlineKeyboardMarkup(menu_build(
		[	#Добавление ботов
			InlineKeyboardButton("LLM", callback_data="menu:llm"),
			InlineKeyboardButton("Image-s", callback_data="menu:text2image"),
			InlineKeyboardButton("Video-s", callback_data="menu:text2video"),
			InlineKeyboardButton("Остальное", callback_data="menu:second2all")
		],
		n_cols=2, #Число кнопок в колонке
		header_buttons=InlineKeyboardButton("⭐ Приветствие", callback_data="menu:helloButton"), #  action:helloButton - уникальная строка с "action:метод"
		footer_buttons=InlineKeyboardButton("Информация о боте", callback_data="menu:buttonInfoBot")
	))

#Создание меню для llm
def create_bot_menu_choice_llm():
	return InlineKeyboardMarkup(menu_build(
		[	#Добавление ботов
			InlineKeyboardButton("chatGPT", callback_data="action:activateChatGPT")
		],
		n_cols=2 #Число кнопок в колонке
	 ))


#Создание меню для разработчика
def create_bot_menu_commands_razrab():
	return InlineKeyboardMarkup(menu_build(
		[	#Добавление ботов
			InlineKeyboardButton("Включить логи", callback_data="commands:start_logs"),
			InlineKeyboardButton("Общее число пользователей", callback_data="commands:list_users")
		],
		n_cols=2 #Число кнопок в колонке
	 ))

