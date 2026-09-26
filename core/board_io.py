"""board.yaml：支援 dict（days.\"1\".lifts）與 list（days[].exercises）兩種 schema。"""

from __future__ import annotations

import copy
import re
from typing import Any

_DAY_ID = re.compile(r"^day(\d+)$", re.I)


def day_id(day_n: int) -> str:
    return f"day{day_n}"


def day_n_from_ref(ref: Any) -> int | None:
    if ref is None:
        return None
    if isinstance(ref, int):
        return ref
    s = str(ref).strip()
    m = _DAY_ID.fullmatch(s)
    if m:
        return int(m.group(1))
    if s.isdigit():
        return int(s)
    return None


def board_uses_list_days(board: dict) -> bool:
    days = board.get("days")
    return isinstance(days, list)


def active_day_n(board: dict) -> int | None:
    return day_n_from_ref(board.get("active_day"))


def find_day_block(board: dict, day_n: int) -> dict | None:
    days = board.get("days")
    if isinstance(days, dict):
        block = days.get(str(day_n)) or days.get(day_n)
        return block if isinstance(block, dict) else None
    if isinstance(days, list):
        want = day_id(day_n)
        for block in days:
            if not isinstance(block, dict):
                continue
            bid = block.get("id") or block.get("day")
            if bid == want or day_n_from_ref(bid) == day_n:
                return block
    return None


def iter_cycle_day_blocks(board: dict) -> list[tuple[int, dict]]:
    days = board.get("days")
    cycle = board.get("microcycle_days")
    if cycle:
        out: list[tuple[int, dict]] = []
        for ref in cycle:
            n = day_n_from_ref(ref)
            if n is None:
                continue
            block = find_day_block(board, n)
            if block:
                out.append((n, block))
        return out
    if isinstance(days, dict):
        return [(int(k), v) for k, v in days.items() if isinstance(v, dict) and str(k).isdigit()]
    if isinstance(days, list):
        out = []
        for block in days:
            if not isinstance(block, dict):
                continue
            n = day_n_from_ref(block.get("id") or block.get("day"))
            if n is not None:
                out.append((n, block))
        return out
    return []


def day_exercises_raw(block: dict) -> list[dict]:
    raw = block.get("exercises") or block.get("lifts") or []
    return raw if isinstance(raw, list) else []


def _load_part(planned: dict) -> str:
    if planned.get("added_kg") is not None:
        return f"+{planned['added_kg']:g}"
    if planned.get("kg") is not None:
        return f"{planned['kg']:g}kg"
    if planned.get("lb") is not None:
        return f"{planned['lb']:g}lb"
    if planned.get("hold_s") is not None:
        return f"{planned['hold_s']:g}s"
    return ""


def goal_from_planned(planned: dict) -> str:
    reps = planned.get("reps")
    sets_n = planned.get("sets")
    load = _load_part(planned)
    rpe = planned.get("rpe")
    if sets_n is not None and reps is not None:
        body = f"{int(sets_n)}×{int(reps)}"
    elif reps is not None:
        body = f"{int(reps)}"
    elif planned.get("hold_s") is not None:
        body = f"{planned['hold_s']:g}s"
    else:
        body = "—"
    if load and "s" not in body:
        body = f"{body}＠{load}"
    elif load and body == "—":
        body = load
    if rpe is not None:
        body = f"{body} @{rpe:g}" if "@" not in body else body
    return body


def _goal_from_set_row(row: dict, planned: dict) -> str | None:
    if row.get("goal"):
        return str(row["goal"])
    reps = row.get("reps") if row.get("reps") is not None else planned.get("reps")
    load = ""
    if row.get("added_kg") is not None:
        load = f"+{row['added_kg']:g}"
    elif row.get("kg") is not None:
        load = f"{row['kg']:g}kg"
    elif planned:
        load = _load_part(planned)
    if reps is not None and load:
        return f"{int(reps)}＠{load}"
    if reps is not None:
        return f"{int(reps)}"
    if planned:
        return goal_from_planned(planned)
    return None


def _done_from_set_row(row: dict) -> str | None:
    if row.get("done"):
        return str(row["done"])
    mark = row.get("mark")
    if mark not in ("ok", "warn", "fix", "miss"):
        return None
    parts: list[str] = []
    if row.get("kg") is not None:
        parts.append(f"{row['kg']:g}kg")
    if row.get("added_kg") is not None:
        parts.append(f"+{row['added_kg']:g}")
    if row.get("lb") is not None:
        parts.append(f"{row['lb']:g}lb")
    if row.get("hold_s") is not None:
        parts.append(f"{row['hold_s']:g}s")
    if row.get("reps") is not None:
        if parts:
            parts.append(f"×{int(row['reps'])}")
        else:
            parts.append(f"{int(row['reps'])}次")
    if row.get("rpe") is not None:
        parts.append(f"@{row['rpe']:g}")
    return " ".join(parts) if parts else None


def normalize_exercise(raw: dict) -> dict:
    key = raw.get("key") or raw.get("id") or ""
    name = raw.get("name") or raw.get("name_zh") or key
    planned = raw.get("planned") or {}
    if not isinstance(planned, dict):
        planned = {}

    rows = raw.get("sets")
    out_sets: list[dict] = []
    if rows:
        for row in rows:
            if isinstance(row, str):
                out_sets.append({"goal": row, "done": None, "mark": "wait"})
                continue
            goal = _goal_from_set_row(row, planned) or goal_from_planned(planned)
            done = _done_from_set_row(row)
            mark = row.get("mark") or "wait"
            if done and mark == "wait":
                mark = "ok"
            out_sets.append({"goal": goal, "done": done, "mark": mark})
        planned_n = int(planned.get("sets") or 0)
        if planned_n > len(out_sets):
            per = goal_from_planned(planned)
            for _ in range(planned_n - len(out_sets)):
                out_sets.append({"goal": per, "done": None, "mark": "wait"})
    elif raw.get("targets"):
        out_sets = [{"goal": g, "done": None, "mark": "wait"} for g in raw["targets"]]
    elif raw.get("plan"):
        out_sets = [{"goal": str(raw["plan"]), "done": None, "mark": "wait"}]
    elif planned:
        per_goal = goal_from_planned(planned)
        n = int(planned.get("sets") or 1)
        out_sets = [{"goal": per_goal, "done": None, "mark": "wait"} for _ in range(n)]
    else:
        out_sets = []

    return {
        "key": key,
        "name": name,
        "sets": out_sets,
        "last_week": list(raw.get("last_week") or []),
        "skipped": bool(raw.get("skipped")),
    }


def normalize_exercises(block: dict) -> list[dict]:
    return [normalize_exercise(x) for x in day_exercises_raw(block)]


def set_active_day(board: dict, day_n: int | None) -> None:
    if day_n is None:
        board["active_day"] = None
        return
    if board_uses_list_days(board):
        board["active_day"] = day_id(day_n)
    else:
        board["active_day"] = day_n


def merge_lifts_into_block(block: dict, lifts: list[dict], originals: list[dict]) -> None:
    """把 session 用 lifts 寫回 block（保留 list schema 的 id／planned）。"""
    by_id = {ex.get("id") or ex.get("key"): ex for ex in originals}
    use_exercises = "exercises" in block or any("id" in ex for ex in originals)
    if use_exercises:
        out_ex: list[dict] = []
        for lift in lifts:
            oid = lift.get("key")
            ex = copy.deepcopy(by_id.get(oid) or {})
            ex["id"] = oid
            if lift.get("name"):
                ex["name_zh"] = lift["name"]
            orig_rows = ex.get("sets") or []
            new_sets = []
            for i, s in enumerate(lift.get("sets") or []):
                if i < len(orig_rows) and isinstance(orig_rows[i], dict):
                    row = copy.deepcopy(orig_rows[i])
                else:
                    row = {"n": i + 1}
                    planned = ex.get("planned") if isinstance(ex.get("planned"), dict) else {}
                    if planned.get("reps") is not None:
                        row["reps"] = planned["reps"]
                    if planned.get("added_kg") is not None:
                        row["added_kg"] = planned["added_kg"]
                row["mark"] = s.get("mark") or "wait"
                if s.get("done"):
                    row["done"] = s["done"]
                new_sets.append(row)
            ex["sets"] = new_sets
            if lift.get("skipped"):
                ex["skipped"] = True
            out_ex.append(ex)
        block["exercises"] = out_ex
    else:
        block["lifts"] = lifts


def write_day_lifts(board: dict, day_n: int, lifts: list[dict], **meta: Any) -> None:
    block = find_day_block(board, day_n)
    originals = day_exercises_raw(block) if block else []
    if block is None:
        if board_uses_list_days(board):
            block = {"id": day_id(day_n), "exercises": []}
            board.setdefault("days", []).append(block)
        else:
            block = {}
            board.setdefault("days", {})[str(day_n)] = block
        originals = []
    merge_lifts_into_block(block, lifts, originals)
    for k, v in meta.items():
        block[k] = v
