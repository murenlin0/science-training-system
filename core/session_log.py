"""當日紀錄：YAML 真源 → 聊天表 + HTML。"""

from __future__ import annotations

from html import escape
from pathlib import Path

import yaml

from core.volume import add_sets, format_landmarks, weights_for

MARK = {"ok": "✅", "warn": "⚠️", "miss": "❌", "wait": "⏳", "fix": "🔧"}


def load_session(path: Path) -> dict:
    if not path.exists():
        return {"week_label": "", "opened_on": None, "days": []}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {"days": []}


def save_session(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def write_html(path: Path, chat_text: str) -> None:
    path.write_text(
        "<!doctype html><meta charset=utf-8><pre>" + escape(chat_text) + "</pre>\n",
        encoding="utf-8",
    )


def tally_week(data: dict) -> tuple[dict[str, float], dict[str, float]]:
    done, week = {}, {}
    for day in data.get("days") or []:
        for lift in day.get("lifts") or []:
            key = lift.get("key") or ""
            sets = lift.get("sets") or []
            add_sets(week, key, float(len(sets)))
            add_sets(done, key, float(sum(1 for s in sets if s.get("mark") in ("ok", "warn", "fix"))))
    return done, week


def format_lift(lift: dict, highlight: int | None = None) -> str:
    name = lift.get("name") or lift.get("key") or "動作"
    ws = weights_for(lift.get("key") or "")
    wline = " ".join(f"{m}{w:g}" for m, w in ws)
    rows = ["| 目標 | 今日 | 上周 |", "|------|------|------|"]
    last = lift.get("last_week") or []
    for i, s in enumerate(lift.get("sets") or []):
        mark = MARK.get(s.get("mark") or "wait", "⏳")
        today = (s.get("done") or "—") + mark
        if highlight is not None and i == highlight:
            today = f"**{today}**"
        prev = last[i] if i < len(last) else "—"
        rows.append(f"| {s.get('goal') or '—'} | {today} | {prev} |")
    block = f"**{name}**\n{wline}" if wline else f"**{name}**"
    return block + "\n" + "\n".join(rows)


def format_day(data: dict, day_n: int, just: tuple[str, int] | None = None) -> str:
    day = next((d for d in data.get("days") or [] if d.get("n") == day_n), None)
    if not day:
        return "沒有這一天的紀錄。"
    parts = [f"{data.get('week_label') or '本週'} · Day {day_n}"]
    for lift in day.get("lifts") or []:
        hi = just[1] if just and lift.get("key") == just[0] else None
        parts.append(format_lift(lift, hi))
    parts.append(format_landmarks(*tally_week(data)))
    return "\n\n".join(parts)
