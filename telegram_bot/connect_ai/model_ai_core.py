from enum import Enum
from typing import Tuple
from dataclasses import dataclass


# Типы моделей
class Model_Type(Enum):
    LLM = 0;
    Text2image = 1
    Text2video = 2

class Data_Type(Enum):
    text  = 0
    image = 1

class Provider_Type(Enum):
    G4f = 1

# Тип модели AI
@dataclass
class ModelAI:
    provider: Provider_Type # Посредник к обращению модели (через duckduckgo, chatgpt4free, transformers, ...)

    model: str;      # Название модели
    kind: Model_Type # Тип модели

    input_data:   Data_Type # Принимает  данные
    output_data:  Data_Type # Возвращает данные

@dataclass
class Bytes_and_type:
    data: bytes
    types: Data_Type


def get_all_modelAI() -> [  ModelAI ]:
    return [
        ModelAI(Provider_Type.G4f, "gpt-4o-mini", Model_Type.LLM, Data_Type.text, Data_Type.image),
        ModelAI(Provider_Type.G4f, "gpt-4", Model_Type.LLM, Data_Type.text, Data_Type.image),
        ModelAI(Provider_Type.G4f, "kimi-k2", Model_Type.LLM, Data_Type.text, Data_Type.image),
        ModelAI(Provider_Type.G4f, "qwen-3-32b", Model_Type.LLM, Data_Type.text, Data_Type.image)
    ]
