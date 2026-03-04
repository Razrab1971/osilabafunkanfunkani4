# connect_ai/llm_core.py
from typing import Tuple, Dict, Any

# 1) Текстовый ответ
async def call_llm_text(prompt: str, settings: dict) -> str:
    provider = settings.get("provider", "stub")
    model = settings.get("model", "default")
    temperature = settings.get("temperature", 0.7)

    # заглушки под 2 LLM (минимум по ТЗ)
    if provider == "stub_fast":
        return f"[LLM:FAST model={model} temp={temperature}] {prompt}"
    return f"[LLM:DEFAULT model={model} temp={temperature}] {prompt}"

# 2) Медиа-ответ (байты + мета). Пока заглушка, но интерфейс по ТЗ есть.
async def call_llm_media(prompt: str, settings: dict) -> Tuple[bytes, Dict[str, Any]]:
    data = prompt.encode("utf-8")
    meta = {"type": "bytes", "note": "stub media"}
    return data, meta