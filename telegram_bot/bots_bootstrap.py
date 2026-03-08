# bots_bootstrap.py
from registry import register_bot, BotSpec
#from bots.llm.llm_ui import activate_llm,
from bots.llm.llm_ui import activate_duckduckgo_llm

from connect_ai.model_ai_core import get_all_modelAI, ModelAI

def register_all_bots() -> None:
    # LLM категория: минимум 1 бот, дальше добавлять легко
    # register_bot("LLM", BotSpec(title="LLM", kind="llm", activate=activate_llm))

    for model in get_all_modelAI():
        register_bot(
            model.model, 
            BotSpec(
                title=model.model, 
                model=model, 
                activate=activate_duckduckgo_llm
            )
        )


