"""主項 → 輔助查表。菜單不是原則；L1 只鎖專項性與主項互斥。"""

from __future__ import annotations

from pathlib import Path

import yaml

from core.classify import primaries

_PATH = Path(__file__).resolve().parents[1] / "config" / "assistance.yaml"
_DATA = None


def _data() -> dict:
    global _DATA
    if _DATA is None:
        _DATA = yaml.safe_load(_PATH.read_text(encoding="utf-8"))
    return _DATA


def reload() -> None:
    global _DATA
    _DATA = None
    _data()


def for_primary(key: str) -> dict:
    maps = _data()["primaries"]
    if key not in maps:
        raise KeyError(
            f"主項 {key!r} 沒有輔助對照表。"
            f"已入庫：{sorted(maps)}"
        )
    return maps[key]


def for_primaries(keys: list[str]) -> dict[str, dict]:
    return {k: for_primary(k) for k in keys}


def forbidden_as_accessory(primary_keys: list[str]) -> set[str]:
    ban: set[str] = set()
    for k in primary_keys:
        row = for_primary(k)
        ban.update(row.get("forbid_as_accessory") or [k])
    return ban


def all_mapped_primary_keys() -> list[str]:
    return sorted(_data()["primaries"])


def assert_every_registrable_primary_has_map() -> None:
    mapped = set(all_mapped_primary_keys())
    missing = [m.key for m in primaries() if m.key not in mapped]
    assert not missing, f"可當主項但沒有輔助表：{missing}"
