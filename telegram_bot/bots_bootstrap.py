# bots_bootstrap.py
from registry import register_bot, BotSpec
from bots.llm.llm_ui import activate_llm

def register_all_bots() -> None:
    # LLM категория: минимум 1 бот, дальше добавлять легко
    register_bot("llm", BotSpec(title="LLM", kind="llm", activate=activate_llm))