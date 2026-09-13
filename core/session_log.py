"""當日紀錄：HTML 真源。聊天表只是渲染。"""

from __future__ import annotations

from html import escape
from html.parser import HTMLParser
from pathlib import Path

import yaml

from core.volume import add_sets, format_landmarks, weights_for

MARK = {"ok": "✅", "warn": "⚠️", "miss": "❌", "wait": "⏳", "fix": "🔧"}
_EMPTY = {"", "—", "-", "null", "None"}


def _html_path(path: Path) -> Path:
    return path if path.suffix == ".html" else path.with_suffix(".html")


def _yaml_path(path: Path) -> Path:
    if path.suffix in {".yaml", ".yml"}:
        return path
    return path.with_suffix(".yaml")


def _cell(value) -> str:
    if value is None or str(value).strip() in _EMPTY:
        return "—"
    return str(value)


def parse_session(html: str) -> dict:
    parser = _SessionParser()
    parser.feed(html)
    parser.close()
    return parser.data


def render_session(data: dict) -> str:
    week = data.get("week_label") or "本週"
    opened = data.get("opened_on") or ""
    parts = [
        "<!doctype html>",
        '<meta charset="utf-8">',
        f"<title>{escape(str(week))}</title>",
        "<style>body{font:16px/1.4 sans-serif;margin:1rem}table{border-collapse:collapse}td,th{border:1px solid #ccc;padding:.3em .6em}h2,h3{margin:1rem 0 .4rem}</style>",
        f'<article data-week="{escape(str(week), quote=True)}" data-opened="{escape(str(opened), quote=True)}">',
        f"<h1>{escape(str(week))}</h1>",
    ]
    for day in data.get("days") or []:
        n = day.get("n")
        parts.append(f'<section data-day="{escape(str(n), quote=True)}">')
        parts.append(f"<h2>Day {escape(str(n))}</h2>")
        for lift in day.get("lifts") or []:
            key = lift.get("key") or ""
            name = lift.get("name") or key or "動作"
            parts.append(
                f'<article data-key="{escape(str(key), quote=True)}" data-name="{escape(str(name), quote=True)}">'
            )
            parts.append(f"<h3>{escape(str(name))}</h3>")
            ws = weights_for(key)
            if ws:
                wline = " ".join(f"{m}{w:g}" for m, w in ws)
                parts.append(f"<p>{escape(wline)}</p>")
            parts.append("<table><thead><tr><th>目標</th><th>今日</th><th>上周</th></tr></thead><tbody>")
            last = lift.get("last_week") or []
            for i, s in enumerate(lift.get("sets") or []):
                mark = s.get("mark") or "wait"
                emoji = MARK.get(mark, "⏳")
                prev = last[i] if i < len(last) else None
                parts.append(
                    f'<tr data-mark="{escape(str(mark), quote=True)}">'
                    f"<td>{escape(_cell(s.get('goal')))}</td>"
                    f"<td>{escape(_cell(s.get('done')))}{emoji}</td>"
                    f"<td>{escape(_cell(prev))}</td></tr>"
                )
            parts.append("</tbody></table></article>")
        parts.append("</section>")
    parts.append("</article>")
    parts.append(f'<pre data-derived="volume">{escape(format_landmarks(*tally_week(data)))}</pre>')
    parts.append("")
    return "\n".join(parts)


def load_session(path: Path) -> dict:
    html_p, yaml_p = _html_path(path), _yaml_path(path)
    if html_p.exists():
        return parse_session(html_p.read_text(encoding="utf-8"))
    if yaml_p.exists():
        return yaml.safe_load(yaml_p.read_text(encoding="utf-8")) or {"days": []}
    return {"week_label": "", "opened_on": None, "days": []}


def save_session(path: Path, data: dict) -> None:
    html_p = _html_path(path)
    html_p.parent.mkdir(parents=True, exist_ok=True)
    html_p.write_text(render_session(data), encoding="utf-8")


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
        today = _cell(s.get("done")) + mark
        if highlight is not None and i == highlight:
            today = f"**{today}**"
        prev = last[i] if i < len(last) and last[i] not in (None, "") else "—"
        rows.append(f"| {_cell(s.get('goal'))} | {today} | {_cell(prev)} |")
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


class _SessionParser(HTMLParser):
    """ponytail: 只認 data-week／data-day／data-key／data-mark 與三欄表。頁腳 volume 不讀。手改格子也能進檔。"""

    def __init__(self) -> None:
        super().__init__()
        self.data: dict = {"week_label": "", "opened_on": None, "days": []}
        self._day: dict | None = None
        self._lift: dict | None = None
        self._row: dict | None = None
        self._col = -1
        self._skip = 0
        self._body = False
        self._text: list[str] = []

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        if a.get("data-derived") or tag == "style":
            self._skip += 1
            return
        if self._skip:
            return
        if tag == "article" and "data-week" in a:
            self.data["week_label"] = a.get("data-week") or ""
            opened = (a.get("data-opened") or "").strip()
            self.data["opened_on"] = opened or None
        elif tag == "section" and "data-day" in a:
            self._day = {"n": int(a["data-day"]), "lifts": []}
            self.data["days"].append(self._day)
        elif tag == "article" and "data-key" in a:
            self._lift = {
                "key": a.get("data-key") or "",
                "name": a.get("data-name") or "",
                "sets": [],
                "last_week": [],
            }
            if self._day is not None:
                self._day["lifts"].append(self._lift)
        elif tag == "tbody":
            self._body = True
        elif tag == "tr" and self._body and self._lift is not None:
            self._row = {"mark": a.get("data-mark") or "wait", "goal": None, "done": None}
            self._col = -1
        elif tag == "td" and self._row is not None:
            self._col += 1
            self._text = []

    def handle_endtag(self, tag):
        if self._skip and tag in {"style", "pre", "footer", "div"}:
            self._skip = max(0, self._skip - 1)
            return
        if tag == "td" and self._row is not None:
            text = "".join(self._text).strip()
            for key, ch in MARK.items():
                if text.endswith(ch):
                    text = text[: -len(ch)].strip()
                    if self._row.get("mark") in (None, "", "wait"):
                        self._row["mark"] = key
                    break
            value = None if text in _EMPTY else text
            if self._col == 0:
                self._row["goal"] = value
            elif self._col == 1:
                self._row["done"] = value
            elif self._col == 2 and self._lift is not None:
                self._lift["last_week"].append(value)
            self._text = []
        elif tag == "tr" and self._row is not None:
            if self._lift is not None:
                self._lift["sets"].append(self._row)
            self._row = None
        elif tag == "tbody":
            self._body = False
        elif tag == "article" and self._lift is not None and self._row is None:
            self._lift = None
        elif tag == "section":
            self._day = None

    def handle_data(self, data):
        if self._skip or self._row is None:
            return
        self._text.append(data)
