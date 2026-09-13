"""肌群 fractional 審計。燈號不當擋門。"""

from __future__ import annotations

from pathlib import Path

import yaml

_DIR = Path(__file__).resolve().parent.parent
_MARK = None
_WEIGHTS = None

DOT = {"below": "⚪", "mev": "🟢", "mav": "🔵", "mrv": "🟠", "over": "🔴"}


def _load():
    global _MARK, _WEIGHTS
    if _MARK is None:
        _MARK = yaml.safe_load((_DIR / "config" / "volume_landmarks.yaml").read_text(encoding="utf-8"))
        _WEIGHTS = yaml.safe_load((_DIR / "config" / "volume_weights.yaml").read_text(encoding="utf-8"))
    return _MARK, _WEIGHTS


def weights_for(key: str) -> list[tuple[str, float]]:
    data = _load()[1]["movements"].get(key) or []
    return [(row["m"], float(row["w"])) for row in data]


def add_sets(bucket: dict[str, float], key: str, n: float) -> None:
    for muscle, w in weights_for(key):
        bucket[muscle] = bucket.get(muscle, 0.0) + n * w


def band(muscle: str, weekly: float) -> str:
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
    lines = list(marks["header"])
    rows = []
    for name, spec in marks["muscles"].items():
        w = weekly.get(name, 0.0)
        d = done.get(name, 0.0)
        rel = w / _span(spec)
        rng = f"{spec['mev'][0]:g}–{spec['mev'][1]:g}/{spec['mav'][0]:g}–{spec['mav'][1]:g}/{spec['mrv'][0]:g}–{spec['mrv'][1]:g}"
        rows.append((rel, f"{name} {rng}  {d:g}/{w:g}{DOT[band(name, w)]}"))
    rows.sort(key=lambda r: -r[0])
    lines.append("　".join(r[1] for r in rows))
    return "\n".join(lines)
