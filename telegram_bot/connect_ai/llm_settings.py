# connect_ai/llm_settings.py
from authenticate_db import get_main_db

DEFAULTS = {"provider": "stub", "model": "default", "temperature": 0.7}

async def ensure_settings_row(user_id: str) -> None:
    db = get_main_db()
    await db.fetch(
        """
        INSERT INTO user_llm_settings(user_id, provider, model, temperature)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (user_id) DO NOTHING
        """,
        user_id, DEFAULTS["provider"], DEFAULTS["model"], DEFAULTS["temperature"]
    )

async def get_llm_settings(user_id: str) -> dict:
    db = get_main_db()
    await ensure_settings_row(user_id)
    rows = await db.fetch("SELECT provider, model, temperature FROM user_llm_settings WHERE user_id=$1", user_id)
    provider, model, temperature = rows[0]
    return {"provider": provider, "model": model, "temperature": float(temperature)}

async def set_llm_provider(user_id: str, provider: str) -> None:
    db = get_main_db()
    await ensure_settings_row(user_id)
    await db.fetch("UPDATE user_llm_settings SET provider=$2 WHERE user_id=$1", user_id, provider)

async def set_llm_model(user_id: str, model: str) -> None:
    db = get_main_db()
    await ensure_settings_row(user_id)
    await db.fetch("UPDATE user_llm_settings SET model=$2 WHERE user_id=$1", user_id, model)

async def set_llm_temperature(user_id: str, temperature: float) -> None:
    db = get_main_db()
    await ensure_settings_row(user_id)
    await db.fetch(
        "UPDATE user_llm_settings SET temperature=$2 WHERE user_id=$1",
        user_id, float(temperature),
    )