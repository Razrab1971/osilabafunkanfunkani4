from typing import Union, List
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from registry import list_bots

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

def create_llm_models_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("LLM: default", callback_data="llm:set_model:default")],
        [InlineKeyboardButton("LLM: fast", callback_data="llm:set_model:fast")],
        [InlineKeyboardButton("⬅️ В меню", callback_data="llm:exit")]
    ])

def create_llm_chat_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ В меню", callback_data="llm:exit")]
    ])


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
    bots = list_bots("llm")
    buttons = [InlineKeyboardButton(spec.title, callback_data=f"bot:activate:{bot_id}") for bot_id, spec in bots]
    buttons.append(InlineKeyboardButton("⬅️ В меню", callback_data="llm:exit"))
    return InlineKeyboardMarkup(menu_build(buttons, n_cols=2))


#Создание меню для разработчика
def create_bot_menu_commands_razrab():
	return InlineKeyboardMarkup(menu_build(
		[	#Добавление ботов
			InlineKeyboardButton("Включить логи", callback_data="commands:start_logs"),
			InlineKeyboardButton("Общее число пользователей", callback_data="commands:list_users")
		],
		n_cols=2 #Число кнопок в колонке
	 ))

def create_llm_settings_menu(current_provider: str, current_model: str, temperature: float):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Провайдер: {current_provider}", callback_data="llm:open_provider")],
        [InlineKeyboardButton(f"Модель: {current_model}", callback_data="llm:open_models")],
        [InlineKeyboardButton(f"Температура: {temperature:.1f}", callback_data="llm:open_temp")],
        [InlineKeyboardButton("➡️ В чат", callback_data="llm:enter_chat")],
        [InlineKeyboardButton("⬅️ В меню", callback_data="llm:exit")],
    ])

def create_llm_temperature_menu(current: float):
    # шаг 0.1 в пределах [0.0..1.0]
    opts = []
    for v in [0.0, 0.2, 0.5, 0.7, 1.0]:
        label = f"{v:.1f}" + (" ✅" if abs(v - current) < 1e-9 else "")
        opts.append([InlineKeyboardButton(label, callback_data=f"llm:set_temp:{v}")])

    opts.append([InlineKeyboardButton("⬅️ Назад", callback_data="llm:settings")])
    return InlineKeyboardMarkup(opts)

def create_llm_provider_menu(current: str):
    providers = ["stub", "stub_fast"]
    rows = []
    for p in providers:
        label = p + (" ✅" if p == current else "")
        rows.append([InlineKeyboardButton(label, callback_data=f"llm:set_provider:{p}")])
    rows.append([InlineKeyboardButton("⬅️ Назад", callback_data="llm:settings")])
    return InlineKeyboardMarkup(rows)

