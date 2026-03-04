async def call_llm(prompt: str, settings: dict) -> str:
    model = settings.get("model", "default")
    temperature = settings.get("temperature", 0.7)
    # заглушка, но уже параметризована
    return f"[LLM:{model} temp={temperature}] {prompt}"