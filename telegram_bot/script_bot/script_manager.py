from __future__ import annotations

import asyncio
from typing import Dict, Optional

from .script_models import ScriptInfo


class ScriptManager:
    """
    1 пользователь = 1 активный скрипт.
    Важно: скрипт может быть "активным" ещё до создания task (пока скачиваем/парсим файл).
    """

    def __init__(self) -> None:
        self._tasks: Dict[int, asyncio.Task] = {}
        self._info: Dict[int, ScriptInfo] = {}

    def is_running(self, user_id: int) -> bool:
        info = self._info.get(user_id)
        return bool(info and getattr(info, "is_running", False))

    def is_cancel_requested(self, user_id: int) -> bool:
        info = self._info.get(user_id)
        # совместимость: если в ScriptInfo нет cancel_requested — считаем False
        return bool(info and getattr(info, "cancel_requested", False))

    def mark_starting(self, user_id: int) -> None:
        """
        Вызываем СРАЗУ, как только приняли .script и начали обработку (скачивание/парсинг),
        чтобы /sexit и повторный /script_run работали корректно.
        """
        info = ScriptInfo(user_id=user_id)
        info.is_running = True
        info.last_error = None
        if hasattr(info, "cancel_requested"):
            info.cancel_requested = False
        self._info[user_id] = info

    def start(self, user_id: int, task: asyncio.Task) -> None:
        self._tasks[user_id] = task

        info = self._info.get(user_id)
        if not info:
            info = ScriptInfo(user_id=user_id)
            self._info[user_id] = info

        info.is_running = True
        if hasattr(info, "cancel_requested"):
            info.cancel_requested = False
        info.last_error = None

        def _cleanup(_t: asyncio.Task) -> None:
            inf = self._info.get(user_id)
            if inf:
                inf.is_running = False
                if _t.cancelled():
                    inf.last_error = "Отменено пользователем"
                else:
                    exc = _t.exception()
                    if exc:
                        inf.last_error = str(exc)
            self._tasks.pop(user_id, None)

        task.add_done_callback(_cleanup)

    def finish(self, user_id: int, last_error: Optional[str] = None) -> None:
        """
        Завершить "раннюю" активность (например ошибка парсинга или отмена до старта task).
        """
        info = self._info.get(user_id)
        if info:
            info.is_running = False
            if last_error:
                info.last_error = last_error

        self._tasks.pop(user_id, None)

    def cancel(self, user_id: int) -> bool:
        """
        Отмена должна сработать даже если task ещё не создан (идёт скачивание/парсинг).
        """
        info = self._info.get(user_id)
        if info and getattr(info, "is_running", False):
            if hasattr(info, "cancel_requested"):
                info.cancel_requested = True
            info.is_running = False  # сразу считаем остановленным (как вы хотели в тестах)

            t = self._tasks.get(user_id)
            if t and not t.done():
                t.cancel()
            return True

        t = self._tasks.get(user_id)
        if t and not t.done():
            t.cancel()
            return True

        return False

    def summary_text(self) -> str:
        if not self._info:
            return "Активных скриптов нет."
        lines = ["Активные/последние скрипты:"]
        for uid, info in self._info.items():
            status = "RUNNING" if self.is_running(uid) else "STOPPED"
            err = f" | last_error={getattr(info, 'last_error', None)}" if getattr(info, "last_error", None) else ""
            lines.append(f"- user_id={uid} status={status}{err}")
        return "\n".join(lines)


SCRIPT_MANAGER = ScriptManager()