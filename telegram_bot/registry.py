from dataclasses import dataclass
from typing import Awaitable, Callable, Dict, List

from connect_ai.model_ai_core import ModelAI, Model_Type


@dataclass
class BotSpec:
    title: str
    model: ModelAI # Базовые настройки модели, что принимает и как себя ведёт

    activate: Callable[..., Awaitable[None]]  # вход в режим (открывает меню/настройки)

REGISTRY: Dict[str, BotSpec] = {}

def register_bot(bot_id: str, spec: BotSpec) -> None:
    REGISTRY[bot_id] = spec

def get_bot(bot_id: str) -> BotSpec | None:
    return REGISTRY.get(bot_id)

def list_bots(kind: Model_Type | None = None) -> List[tuple[str, BotSpec]]:
    items = list(REGISTRY.items())
    if kind is None:
        return items
    return [(bot_id, spec) for bot_id, spec in items if spec.model.kind == kind]
