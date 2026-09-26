"""肌群 fractional 審計。燈號不當擋門。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

_DIR = Path(__file__).resolve().parent.parent
_MARK = None
_WEIGHTS = None

DOT = {"below": "⚪", "mev": "🟢", "mav": "🔵", "mrv": "🟠", "over": "🔴"}

# 寫死：Volume 頁腳／權重唯一允許的肌群名。改清單須使用者明確同意。
ALLOWED_MUSCLES = frozenset({
    "前三角", "中三角", "後三角", "胸", "背闊", "二頭", "三頭",
    "股四", "股二", "臀", "小腿", "腹",
})


def reset_cache() -> None:
    global _MARK, _WEIGHTS
    _MARK = None
    _WEIGHTS = None


def _read_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _valid_landmarks(data: Any) -> bool:
    return isinstance(data, dict) and "header" in data and "muscles" in data


def _valid_weights(data: Any) -> bool:
    return isinstance(data, dict) and "movements" in data


def _load():
    global _MARK, _WEIGHTS
    if _MARK is None:
        cfg_lm = _DIR / "config" / "volume_landmarks.yaml"
        cfg_w = _DIR / "config" / "volume_weights.yaml"
        user_lm = _DIR / "user" / "volume_landmarks.yaml"
        user_w = _DIR / "user" / "volume_weights.yaml"

        mark_data = _read_yaml(cfg_lm)
        if user_lm.is_file():
            overlay = _read_yaml(user_lm)
            if _valid_landmarks(overlay):
                mark_data = overlay

        weight_data = _read_yaml(cfg_w)
        if user_w.is_file():
            overlay = _read_yaml(user_w)
            if _valid_weights(overlay):
                weight_data = overlay

        muscles = mark_data.get("muscles") or {}
        mark_data["muscles"] = {k: v for k, v in muscles.items() if k in ALLOWED_MUSCLES}
        for key, rows in list((weight_data.get("movements") or {}).items()):
            weight_data["movements"][key] = [
                r for r in rows if r.get("m") in ALLOWED_MUSCLES
            ]
        _MARK = mark_data
        _WEIGHTS = weight_data
    return _MARK, _WEIGHTS


def weights_for(key: str) -> list[tuple[str, float]]:
    data = _load()[1]["movements"].get(key) or []
    return [(row["m"], float(row["w"])) for row in data if row.get("m") in ALLOWED_MUSCLES]


def add_sets(bucket: dict[str, float], key: str, n: float) -> None:
    for muscle, w in weights_for(key):
        bucket[muscle] = bucket.get(muscle, 0.0) + n * w


def band(muscle: str, weekly: float) -> str:
    if weekly <= 0:
        return "below"
    spec = _load()[0]["muscles"][muscle]
    mev0, mav0, mrv0, mrv1 = spec["mev"][0], spec["mav"][0], spec["mrv"][0], spec["mrv"][1]
    if weekly < mev0:
        return "below"
    if weekly < mav0:
        return "mev"
    if weekly < mrv0:
        return "mav"
    if weekly <= mrv1:
        return "mrv"
    return "over"


def _span(spec: dict) -> float:
    return max(spec["mrv"][1] - spec["mev"][0], 0.01)


def format_landmarks(done: dict[str, float], weekly: dict[str, float]) -> str:
    marks, _ = _load()
    lines = ["Volume Landmark區"]
    lines.extend(marks["header"])
    rows = []
    for name, spec in marks["muscles"].items():
        w = weekly.get(name, 0.0)
        d = done.get(name, 0.0)
        rel = w / _span(spec)
        rng = f"{spec['mev'][0]:g}–{spec['mev'][1]:g}/{spec['mav'][0]:g}–{spec['mav'][1]:g}/{spec['mrv'][0]:g}–{spec['mrv'][1]:g}"
        rows.append((rel, f"{name} {rng}  {d:g}/{w:g}{DOT[band(name, w)]}"))
    rows.sort(key=lambda r: -r[0])
    lines.extend(r[1] for r in rows)
    return "\n".join(lines)


def _count_lift_sets(
    lift: dict,
    *,
    for_weekly: bool,
) -> tuple[float, float]:
    """Return (done_equiv_sets, weekly_equiv_sets) for one lift row on the board."""
    from core.board_io import normalize_exercise

    norm = normalize_exercise(lift)
    key = norm.get("key") or ""
    if not weights_for(key):
        return 0.0, 0.0

    sets = norm.get("sets") or []
    logged = sum(
        1
        for s in sets
        if s.get("mark") in ("ok", "warn", "fix", "miss") or s.get("done")
    )
    if norm.get("skipped") and logged == 0:
        return 0.0, 0.0

    if for_weekly:
        planned = float(len(sets))
    else:
        planned = 0.0

    done = float(
        sum(1 for s in sets if s.get("mark") in ("ok", "warn", "fix"))
    )
    return done, planned


def tally_from_board(board: dict) -> tuple[dict[str, float], dict[str, float]]:
    """
    Weekly denominator = planned sets on all microcycle days on the board.
    Skip-day: unfinished sets on partially logged lifts still count.
    Exercise skipped before any logged set → exclude its planned sets.
    """
    from core.board_io import day_exercises_raw, iter_cycle_day_blocks

    done: dict[str, float] = {}
    weekly: dict[str, float] = {}
    for _n, block in iter_cycle_day_blocks(board):
        for raw in day_exercises_raw(block):
            if not isinstance(raw, dict):
                continue
            d_n, w_n = _count_lift_sets(raw, for_weekly=True)
            key = raw.get("key") or raw.get("id") or ""
            norm_key = key
            if not weights_for(norm_key):
                continue
            if w_n:
                add_sets(weekly, norm_key, w_n)
            if d_n:
                add_sets(done, norm_key, d_n)
    return done, weekly
