from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class StepKind(str, Enum):
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    PRINT = "PRINT"
    ADD = "ADD"
    BOT = "BOT"


@dataclass
class ScriptStep:
    kind: StepKind
    raw: str
    arg_type: Optional[str] = None      # текст/изображение и т.п.
    text: Optional[str] = None          # для PRINT/ADD
    bot_name: Optional[str] = None      # для BOT


@dataclass
class ScriptInfo:
    user_id: int
    is_running: bool = False
    last_error: Optional[str] = None
    cancel_requested: bool = False