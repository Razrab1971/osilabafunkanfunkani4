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



#Функция для показа меню ботов
def create_bot_menu():
	return InlineKeyboardMarkup(menu_build(
		[	#Добавление ботов
			InlineKeyboardButton("chatGPT", callback_data="action:activateChatGPT")
		],
		n_cols=1, #Число кнопок в колонке
		header_buttons=InlineKeyboardButton("⭐ Приветствие", callback_data="action:helloButton") #  action:helloButton - уникальная строка с "action:метод"
	))
