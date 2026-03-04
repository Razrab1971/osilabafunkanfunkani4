from __future__ import annotations

import re
from typing import List
from .script_models import ScriptStep, StepKind


_BLOCK_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
_LINE_COMMENT_RE = re.compile(r"//.*?$", re.MULTILINE)

# NAME(type)   или  PRINT("text")   или ADD("text"%)
_CALL_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*\(\s*(.*?)\s*\)\s*$")


def _strip_comments(text: str) -> str:
    text = _BLOCK_COMMENT_RE.sub("", text)
    text = _LINE_COMMENT_RE.sub("", text)
    return text


def _join_lines(text: str) -> str:
    # Склеиваем строки с "\" (переносы)
    lines = text.splitlines()
    out = []
    buff = ""
    for line in lines:
        line = line.rstrip()
        if not line:
            continue
        if line.endswith("\\"):
            buff += line[:-1] + " "
        else:
            out.append(buff + line)
            buff = ""
    if buff.strip():
        out.append(buff.strip())
    return "\n".join(out)


def _split_pipeline(text: str) -> List[str]:
    # делим по | (простая версия)
    parts = [p.strip() for p in text.split("|")]
    return [p for p in parts if p]


def _parse_string_literal(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and ((s[0] == '"' and s[-1] == '"') or (s[0] == "'" and s[-1] == "'")):
        return s[1:-1]
    return s


def parse_script(script_text: str) -> List[ScriptStep]:
    cleaned = _join_lines(_strip_comments(script_text)).strip()
    if not cleaned:
        raise ValueError("Пустой скрипт")

    all_steps: List[ScriptStep] = []

    for line in cleaned.splitlines():
        line = line.strip()
        if not line:
            continue

        parts = _split_pipeline(line)
        for part in parts:
            m = _CALL_RE.match(part)
            if not m:
                raise ValueError(f"Не понимаю шаг: {part}")

            name = m.group(1)
            inside = m.group(2).strip()
            upper = name.upper()

            if upper == "INPUT":
                # INPUT(текст)
                all_steps.append(ScriptStep(kind=StepKind.INPUT, raw=part, arg_type=inside or "текст"))

            elif upper == "OUTPUT":
                # OUTPUT(текст)
                all_steps.append(ScriptStep(kind=StepKind.OUTPUT, raw=part, arg_type=inside or "текст"))

            elif upper == "PRINT":
                # PRINT("...")
                text = _parse_string_literal(inside)
                all_steps.append(ScriptStep(kind=StepKind.PRINT, raw=part, text=text))

            elif upper == "ADD":
                # Поддержка двух вариантов:
                # 1) ADD("...%")    (процент внутри кавычек)
                # 2) ADD("... "%)   (процент СНАРУЖИ кавычек, как в ТЗ)
                arg = inside.strip()
                percent_outside = arg.endswith("%")
                if percent_outside:
                    arg = arg[:-1].rstrip()

                text = _parse_string_literal(arg)

                # если % был снаружи — возвращаем его как маркер подстановки
                if percent_outside:
                    text = text + "%"

                all_steps.append(ScriptStep(kind=StepKind.ADD, raw=part, text=text))

            else:
                # BotName(тип)
                all_steps.append(ScriptStep(kind=StepKind.BOT, raw=part, bot_name=name, arg_type=inside or "текст"))

    # Валидация: INPUT обязателен, OUTPUT НЕ обязателен (по ТЗ)
    if not any(s.kind == StepKind.INPUT for s in all_steps):
        raise ValueError("Нет INPUT(.) в скрипте")

    return all_steps