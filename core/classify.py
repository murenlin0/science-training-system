"""動作分類：key → 類型 P / B / I。資料在 movements.yaml。"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

import yaml

ISOMETRIC_WORK_PCT_CAP = 70.0
_DIR = Path(__file__).resolve().parent


class MovementType(str, Enum):
    PURE = "P"
    BODYWEIGHT = "B"
    ISOMETRIC = "I"


@dataclass
class Movement:
    key: str
    name_zh: str
    name_en: str
    mtype: MovementType
    mev: Optional[float] = None
    mav: Optional[float] = None
    mrv: Optional[float] = None
    weekly_cap: Optional[float] = None
    min_gap_hours: int = 48
    increment_pct_cap: float = 2.5
    allow_failure: bool = False
    can_be_primary: bool = False
    notes: str = ""
    tags: list = field(default_factory=list)

    def is_bodyweight(self) -> bool:
        return self.mtype == MovementType.BODYWEIGHT

    def is_isometric(self) -> bool:
        return self.mtype == MovementType.ISOMETRIC


def _load_movements() -> dict[str, Movement]:
    raw = yaml.safe_load((_DIR / "movements.yaml").read_text(encoding="utf-8"))
    out = {}
    for spec in raw["movements"]:
        spec = dict(spec)
        key = spec["key"]
        mtype = MovementType(str(spec.pop("type")).upper())
        spec.pop("key")
        out[key] = Movement(key=key, mtype=mtype, **spec)
    return out


def _load_ladders() -> dict:
    raw = yaml.safe_load((_DIR / "ladders.yaml").read_text(encoding="utf-8"))
    return raw["ladders"]


REGISTRY = _load_movements()
ISOMETRIC_LADDERS = _load_ladders()


def get(key: str) -> Movement:
    if key not in REGISTRY:
        raise KeyError(
            f"動作 {key!r} 不在註冊表中。"
            f"目前已註冊：{sorted(REGISTRY)}"
        )
    return REGISTRY[key]


def register(movement: Movement, overwrite: bool = False) -> None:
    if movement.key in REGISTRY and not overwrite:
        raise ValueError(f"動作 {movement.key!r} 已存在。要覆寫請傳 overwrite=True。")
    REGISTRY[movement.key] = movement


def register_from_dict(spec: dict, overwrite: bool = False) -> Movement:
    missing = [f for f in ("key", "name_zh", "name_en", "type") if f not in spec]
    if missing:
        raise ValueError(f"自訂動作缺少必填欄位：{missing}")
    spec = dict(spec)
    raw_type = spec.pop("type")
    try:
        mtype = MovementType(str(raw_type).upper())
    except ValueError:
        raise ValueError(
            f"動作 {spec['key']!r} 的 type={raw_type!r} 無效。須為 P／B／I"
        )
    allowed = set(Movement.__dataclass_fields__) - {"mtype"}
    unknown = set(spec) - allowed
    if unknown:
        raise ValueError(f"動作 {spec['key']!r} 有未知欄位：{sorted(unknown)}")
    mv = Movement(mtype=mtype, **spec)
    register(mv, overwrite=overwrite)
    return mv


def by_type(mtype: MovementType) -> list:
    return [m for m in REGISTRY.values() if m.mtype == mtype]


def primaries() -> list[Movement]:
    return [m for m in REGISTRY.values() if m.can_be_primary]


def ladder_factor(ladder_name: str, variant_key: str) -> float:
    for row in ISOMETRIC_LADDERS.get(ladder_name, []):
        if row[0] == variant_key:
            return float(row[3])
    raise KeyError(
        f"等長階梯 {ladder_name!r} 中找不到變式 {variant_key!r}。"
        f"可用：{[r[0] for r in ISOMETRIC_LADDERS.get(ladder_name, [])]}"
    )


def next_variant(ladder_name: str, variant_key: str) -> Optional[tuple]:
    ladder = ISOMETRIC_LADDERS.get(ladder_name, [])
    for i, row in enumerate(ladder):
        if row[0] == variant_key:
            return tuple(ladder[i + 1]) if i + 1 < len(ladder) else None
    raise KeyError(f"等長階梯 {ladder_name!r} 中找不到變式 {variant_key!r}")
