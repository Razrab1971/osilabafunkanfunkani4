from __future__ import annotations

import os
import asyncio
import logging
from telegram import Update
from telegram.ext import ContextTypes

from .script_parser import parse_script
from .script_models import StepKind
from .script_manager import SCRIPT_MANAGER

from authenticate_db import get_user_id, check_user_no_pro, get_main_db


# --- Простая "эмуляция" вызова ботов ---
# Потом заменишь на реальный connect-AI.
async def _call_bot(bot_name: str, text: str) -> str:
    return f"[{bot_name}] {text}"


async def _execute_steps(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    steps,
    user_input: str,
    user_id: str
) -> None:
    """
    Исполнение DSL шагов.
    Важно: никаких try/except здесь не нужно.
    Останов: через SCRIPT_MANAGER.is_cancel_requested(user_id).
    """
    chat_id = update.effective_chat.id

    # Даём циклу событий шанс обработать /sexit
    await asyncio.sleep(0)

    if SCRIPT_MANAGER.is_cancel_requested(user_id):
        return

    last_output = ""
    add_context = ""
    had_output = False

    for step in steps:
        # мгновенно прекращаем любые действия после /sexit
        if SCRIPT_MANAGER.is_cancel_requested(user_id):
            return

        if step.kind == StepKind.INPUT:
            last_output = user_input

        elif step.kind == StepKind.ADD:
            t = step.text or ""
            if "%" in t:
                add_context = t.replace("%", last_output)
            else:
                add_context = t + last_output

        elif step.kind == StepKind.PRINT:
            if SCRIPT_MANAGER.is_cancel_requested(user_id):
                return
            await context.bot.send_message(chat_id=chat_id, text=step.text or "")

        elif step.kind == StepKind.BOT:
            payload = (add_context + last_output) if add_context else last_output
            add_context = ""
            # если отменили — не вызываем бота
            if SCRIPT_MANAGER.is_cancel_requested(user_id):
                return
            last_output = await _call_bot(step.bot_name or "NoName", payload)

        elif step.kind == StepKind.OUTPUT:
            had_output = True

            if SCRIPT_MANAGER.is_cancel_requested(user_id):
                return

            out_type = (step.arg_type or "текст").lower()
            if "текст" in out_type:
                await context.bot.send_message(chat_id=chat_id, text=last_output)
            else:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"OUTPUT({step.arg_type}) пока не реализован, выводим текст:\n{last_output}",
                )

        await asyncio.sleep(0)  # чтобы cancel отрабатывал корректно

    if not had_output:
        if SCRIPT_MANAGER.is_cancel_requested(user_id):
            return
        await context.bot.send_message(chat_id=chat_id, text="Скрипт завершён, но OUTPUT не задан.")


async def general_script_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("general script cmd called")

    base_dir = os.path.dirname(__file__)
    path = os.path.join(base_dir, "example", "general.script")

    if not os.path.exists(path):
        await update.message.reply_text(
            "Файл example/general.script не найден. "
            "Создай telegram_bot/script_bot/example/general.script"
        )
        return

    with open(path, "rb") as fp:
        await update.message.reply_document(
            document=fp,
            filename="general.script",
            caption="Шаблон скрипта. Используй /script_run и пришли .script как документ (можно с подписью — это будет INPUT).",
        )


async def script_run_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /script_run — переводим пользователя в режим ожидания файла .script
    """
    uid = get_user_id(update)

    # Уже ждём файл — не надо повторно включать режим
    if context.user_data.get("await_script_file"):
        await update.message.reply_text(
            "Я уже жду от тебя .script файл. Пришли его документом или отмени ожидание командой /sexit."
        )
        return

    # Уже выполняется (или стартует) скрипт
    if SCRIPT_MANAGER.is_running(uid):
        await update.message.reply_text(
            "У тебя уже выполняется скрипт. Останови его командой /sexit."
        )
        return

    context.user_data["await_script_file"] = True
    await update.message.reply_text("Ок. Пришли мне .script файлом (как документ).")


async def sexit_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Отменяет ожидание .script и/или останавливает активный скрипт.
    """
    uid = get_user_id(update)

    # 1) Если мы просто ждём файл — это тоже "активное состояние"
    if context.user_data.get("await_script_file"):
        context.user_data["await_script_file"] = False
        await update.message.reply_text("Ожидание .script отменено.")
        return

    # 2) Если идёт выполнение/старт — отменяем через менеджер
    ok = SCRIPT_MANAGER.cancel(uid)
    await update.message.reply_text("Скрипт отменён." if ok else "Активного скрипта нет.")


async def on_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Ловим файл .script, когда пользователь вызвал /script_run
    """

    logging.info("Ждем-с on_document ?")

    if not context.user_data.get("await_script_file"):
        if await check_user_no_pro(get_main_db(), update):
            return
        context.user_data["await_script_file"] = True


    doc = update.message.document
    if not doc:
        return

    if not (doc.file_name or "").endswith(".script"):
        await update.message.reply_text("Нужен файл с расширением .script")
        return

    uid = get_user_id(update)
    SCRIPT_MANAGER.mark_starting(uid)

    if SCRIPT_MANAGER.is_cancel_requested(uid):
        SCRIPT_MANAGER.finish(uid, "Отменено пользователем")
        context.user_data["await_script_file"] = False
        await update.message.reply_text("Скрипт отменён.")
        return

    # Скачиваем во временную папку бота
    file = await doc.get_file()
    tmp_dir = "/tmp"
    os.makedirs(tmp_dir, exist_ok=True)
    local_path = os.path.join(tmp_dir, f"{uid}_{doc.file_name}")

    await file.download_to_drive(custom_path=local_path)

    if SCRIPT_MANAGER.is_cancel_requested(uid):
        context.user_data["await_script_file"] = False
        SCRIPT_MANAGER.finish(uid, last_error="Отменено до старта")
        return

    # Считываем и парсим
    try:
        with open(local_path, "r", encoding="utf-8") as f:
            script_text = f.read()
        steps = parse_script(script_text)
        if SCRIPT_MANAGER.is_cancel_requested(uid):
            context.user_data["await_script_file"] = False
            SCRIPT_MANAGER.finish(uid, last_error="Отменено до старта")
            return
        if SCRIPT_MANAGER.is_cancel_requested(uid):
            SCRIPT_MANAGER.finish(uid, "Отменено пользователем")
            await update.message.reply_text("Скрипт отменён.")
            return
    except Exception as e:
        context.user_data["await_script_file"] = False
        SCRIPT_MANAGER.finish(uid, f"Ошибка парсинга: {e}")
        await update.message.reply_text(f"Ошибка парсинга скрипта: {e}")
        return

    context.user_data["await_script_file"] = False

    # Берём ввод пользователя: либо из подписи к файлу, либо дефолт
    user_input = (update.message.caption or "").strip()

    await update.message.reply_text("Запускаю выполнение...")

    task = asyncio.create_task(_execute_steps(update, context, steps, user_input, uid))
    SCRIPT_MANAGER.start(uid, task)
