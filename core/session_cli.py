"""當日開練／跳過／回報組／Volume 的固定管線。Skill 先呼叫 CLI，再在 prose 做 Δ 調整。"""

from __future__ import annotations

import argparse
import copy
import re
import sys
from datetime import date
from pathlib import Path

import yaml

from core.board_io import (
    active_day_n,
    find_day_block,
    normalize_exercise,
    normalize_exercises,
    set_active_day,
    write_day_lifts,
)
from core.session_log import format_day_board, load_session, save_session
from core.volume import format_landmarks, tally_from_board

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _read_yaml(path: Path) -> dict:
    if not path.is_file():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def _parse_day(day: str) -> int:
    m = re.fullmatch(r"day(\d+)", day.strip(), re.I)
    if not m:
        raise SystemExit(f"invalid --day: {day!r} (want dayN)")
    return int(m.group(1))


def load_board(user_dir: Path) -> dict:
    return _read_yaml(user_dir / "board.yaml")


def save_board(user_dir: Path, board: dict) -> None:
    _write_yaml(user_dir / "board.yaml", board)


def _lift_logged_count(lift: dict) -> int:
    return sum(
        1
        for s in lift.get("sets") or []
        if s.get("mark") in ("ok", "warn", "fix", "miss") or s.get("done")
    )


def _session_path(user_dir: Path) -> Path:
    return user_dir / "session"


def cmd_open_day(user_dir: Path, day_n: int, opened_on: str | None) -> None:
    board = load_board(user_dir)
    if not board.get("days"):
        raise SystemExit("board.yaml has no days")
    block = find_day_block(board, day_n)
    if not block:
        raise SystemExit(f"no day block for day{day_n}")
    lifts = normalize_exercises(block)
    if not lifts:
        raise SystemExit(f"no lifts planned for day {day_n}")

    last_week_day = block.get("last_week_day") or board.get("last_week_day")

    session = {
        "week_label": board.get("week_label") or "本週",
        "opened_on": opened_on or date.today().isoformat(),
        "active_day": day_n,
        "days": [{"n": day_n, "last_week_day": last_week_day, "lifts": lifts}],
    }
    save_session(_session_path(user_dir), session)

    write_day_lifts(board, day_n, lifts, last_week_day=last_week_day)
    set_active_day(board, day_n)
    save_board(user_dir, board)

    print(format_day_board(session, day_n, sort_lifts=True, board_for_volume=board))


def _archive_session(user_dir: Path, day_n: int) -> None:
    path = _session_path(user_dir)
    data = load_session(path)
    if not data.get("days"):
        return
    out = user_dir / f"session_day{day_n}.yaml"
    _write_yaml(out, data)


def cmd_skip_day(
    user_dir: Path,
    day_n: int,
    reason: str,
    at: str,
    open_day: int | None,
) -> None:
    board = load_board(user_dir)
    if active_day_n(board) == day_n:
        _archive_session(user_dir, day_n)

    block = find_day_block(board, day_n)
    if not block:
        raise SystemExit(f"no day block for day{day_n}")
    lifts = normalize_exercises(block)
    for lift in lifts:
        logged = _lift_logged_count(lift)
        for s in lift.get("sets") or []:
            if s.get("mark") in ("ok", "warn", "fix", "miss") or s.get("done"):
                continue
            s["mark"] = "skip"
        if logged == 0:
            lift["skipped"] = True

    write_day_lifts(
        board,
        day_n,
        lifts,
        skip_reason=reason,
        skipped_at=at,
    )
    set_active_day(board, None)
    save_board(user_dir, board)

    if open_day is not None:
        cmd_open_day(user_dir, open_day, at)


def _format_done(
    reps: int | None,
    rpe: float | None,
    kg: float | None,
    added_kg: float | None,
    hold_s: float | None,
    lb: float | None,
) -> str:
    parts: list[str] = []
    if kg is not None:
        parts.append(f"{kg:g}kg")
    if added_kg is not None:
        parts.append(f"+{added_kg:g}")
    if lb is not None:
        parts.append(f"{lb:g}lb")
    if hold_s is not None:
        parts.append(f"{hold_s:g}s")
    if reps is not None:
        if parts:
            parts.append(f"×{reps}")
        else:
            parts.append(f"{reps}次")
    if rpe is not None:
        parts.append(f"@{rpe:g}")
    return " ".join(parts) if parts else "—"


def _find_lift(lifts: list[dict], exercise: str) -> dict | None:
    for lift in lifts:
        if lift.get("key") == exercise or lift.get("name") == exercise:
            return lift
    return None


def _next_wait_index(lift: dict) -> int | None:
    for i, s in enumerate(lift.get("sets") or []):
        if s.get("mark") in (None, "", "wait"):
            return i
    return None


def cmd_log_set(
    user_dir: Path,
    exercise: str,
    set_n: int | None,
    reps: int | None,
    rpe: float | None,
    kg: float | None,
    added_kg: float | None,
    hold_s: float | None,
    lb: float | None,
) -> None:
    board = load_board(user_dir)
    day_n = active_day_n(board)
    if not day_n:
        raise SystemExit("no active_day on board; run open-day first")

    session = load_session(_session_path(user_dir))
    day = next((d for d in session.get("days") or [] if d.get("n") == day_n), None)
    if not day:
        raise SystemExit("session missing active day")

    lifts = day.get("lifts") or []
    lift = _find_lift(lifts, exercise)
    if not lift:
        raise SystemExit(f"exercise not on today's board: {exercise}")

    idx = (set_n - 1) if set_n is not None else _next_wait_index(lift)
    if idx is None or idx < 0 or idx >= len(lift.get("sets") or []):
        raise SystemExit("no set slot to log")

    done = _format_done(reps, rpe, kg, added_kg, hold_s, lb)
    lift["sets"][idx]["done"] = done
    lift["sets"][idx]["mark"] = "ok"

    write_day_lifts(board, day_n, lifts)
    save_board(user_dir, board)

    save_session(_session_path(user_dir), session)

    print(
        format_day_board(
            session,
            day_n,
            sort_lifts=True,
            highlight=(lift.get("key") or exercise, idx),
            board_for_volume=board,
        )
    )

    nxt = _next_wait_index(lift)
    if nxt is not None:
        goal = lift["sets"][nxt].get("goal") or "—"
        print()
        print(f"下一組提示：計畫目標 {goal}（Δ／RPE 自調見 session-adjust.md）")


def cmd_volume(user_dir: Path) -> None:
    board = load_board(user_dir)
    done, weekly = tally_from_board(board)
    print(format_landmarks(done, weekly))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="python -m core.session_cli")
    sub = p.add_subparsers(dest="cmd", required=True)

    o = sub.add_parser("open-day", help="開練：寫 session + 印整表")
    o.add_argument("--user-dir", type=Path, required=True)
    o.add_argument("--day", required=True)
    o.add_argument("--date", dest="opened_on", default=None)

    s = sub.add_parser("skip-day", help="跳過日；可選接 open-day")
    s.add_argument("--user-dir", type=Path, required=True)
    s.add_argument("--day", required=True)
    s.add_argument("--reason", required=True)
    s.add_argument("--at", required=True)
    s.add_argument("--open", dest="open_day", default=None, help="dayM to open after skip")

    l = sub.add_parser("log-set", help="回報一組")
    l.add_argument("--user-dir", type=Path, required=True)
    l.add_argument("--exercise", required=True)
    l.add_argument("--set", type=int, default=None)
    l.add_argument("--reps", type=int, default=None)
    l.add_argument("--rpe", type=float, default=None)
    l.add_argument("--kg", type=float, default=None)
    l.add_argument("--added-kg", type=float, default=None)
    l.add_argument("--hold-s", type=float, default=None)
    l.add_argument("--lb", type=float, default=None)

    v = sub.add_parser("volume", help="仅印 Volume Landmark 區")
    v.add_argument("--user-dir", type=Path, required=True)

    return p


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    user_dir = args.user_dir.expanduser().resolve()

    if args.cmd == "open-day":
        cmd_open_day(user_dir, _parse_day(args.day), args.opened_on)
    elif args.cmd == "skip-day":
        open_n = _parse_day(args.open_day) if args.open_day else None
        cmd_skip_day(user_dir, _parse_day(args.day), args.reason, args.at, open_n)
    elif args.cmd == "log-set":
        cmd_log_set(
            user_dir,
            args.exercise,
            args.set,
            args.reps,
            args.rpe,
            args.kg,
            args.added_kg,
            args.hold_s,
            args.lb,
        )
    elif args.cmd == "volume":
        cmd_volume(user_dir)
    else:
        raise SystemExit(f"unknown command {args.cmd}")


if __name__ == "__main__":
    main(sys.argv[1:])
