"""session_cli 開練／跳過／回報／Volume。"""

from pathlib import Path

import yaml

from core.session_cli import main
from core.volume import tally_from_board


def _fixture_board(user_dir: Path) -> None:
    user_dir.mkdir(parents=True)
    board = {
        "week_label": "第1周",
        "microcycle_days": [1, 2],
        "active_day": None,
        "days": {
            "1": {
                "last_week_day": 2,
                "lifts": [
                    {
                        "key": "ohp",
                        "name": "肩推",
                        "sets": [
                            {"goal": "35×5 @8"},
                            {"goal": "35×5 @8"},
                        ],
                        "last_week": ["30×5", "—"],
                    },
                    {
                        "key": "rotator_90_90",
                        "name": "90/90 內外旋",
                        "sets": [{"goal": "15×各 @6"}],
                    },
                ],
            },
            "2": {
                "lifts": [
                    {
                        "key": "ohp",
                        "name": "肩推",
                        "sets": [{"goal": "32×5 @7"}],
                    },
                ],
            },
        },
    }
    (user_dir / "board.yaml").write_text(
        yaml.dump(board, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


def test_open_day_creates_session_and_volume_title(tmp_path, capsys):
    ud = tmp_path / "user"
    _fixture_board(ud)
    main(["open-day", "--user-dir", str(ud), "--day", "day1", "--date", "2026-09-26"])
    out = capsys.readouterr().out
    assert "Volume Landmark區" in out
    assert "肩推" in out
    assert (ud / "session.html").is_file()
    data = yaml.safe_load((ud / "board.yaml").read_text(encoding="utf-8"))
    assert data["active_day"] == 1


def test_skip_day_preserves_logged_and_can_open_next(tmp_path, capsys):
    ud = tmp_path / "user"
    _fixture_board(ud)
    main(["open-day", "--user-dir", str(ud), "--day", "day1"])
    main(
        [
            "log-set",
            "--user-dir",
            str(ud),
            "--exercise",
            "ohp",
            "--reps",
            "5",
            "--rpe",
            "8",
            "--kg",
            "35",
        ]
    )
    main(
        [
            "skip-day",
            "--user-dir",
            str(ud),
            "--day",
            "day1",
            "--reason",
            "時間不夠",
            "--at",
            "2026-09-26",
            "--open",
            "day2",
        ]
    )
    board = yaml.safe_load((ud / "board.yaml").read_text(encoding="utf-8"))
    day1 = board["days"]["1"]["lifts"][0]
    assert day1["sets"][0]["done"] is not None
    assert day1["sets"][1]["mark"] == "skip"
    assert (ud / "session_day1.yaml").is_file()
    assert board["active_day"] == 2
    out = capsys.readouterr().out
    assert "Day 2" in out


def test_log_set_increments_done_tally(tmp_path):
    ud = tmp_path / "user"
    _fixture_board(ud)
    main(["open-day", "--user-dir", str(ud), "--day", "day1"])
    main(
        [
            "log-set",
            "--user-dir",
            str(ud),
            "--exercise",
            "ohp",
            "--reps",
            "5",
            "--rpe",
            "8",
            "--kg",
            "35",
        ]
    )
    board = yaml.safe_load((ud / "board.yaml").read_text(encoding="utf-8"))
    done, weekly = tally_from_board(board)
    assert weekly.get("前三角", 0) >= 2.0
    assert done.get("前三角", 0) == 1.0


def test_volume_excludes_empty_weight_keys(tmp_path, capsys):
    ud = tmp_path / "user"
    _fixture_board(ud)
    main(["open-day", "--user-dir", str(ud), "--day", "day1"])
    main(["volume", "--user-dir", str(ud)])
    out = capsys.readouterr().out
    assert "rotator_90_90" not in out
    board = yaml.safe_load((ud / "board.yaml").read_text(encoding="utf-8"))
    done, weekly = tally_from_board(board)
    assert done == done  # smoke
    assert weekly.get("前三角") == 2.0 + 1.0  # day1 + day2 planned ohp sets


def _fixture_list_board(user_dir: Path) -> None:
    user_dir.mkdir(parents=True)
    board = {
        "week_label": "第1周",
        "microcycle_days": ["day1", "day3"],
        "active_day": "day3",
        "days": [
            {
                "id": "day1",
                "title": "引體",
                "last_week_day": 1,
                "exercises": [
                    {
                        "id": "weighted_pullup",
                        "name_zh": "負重引體",
                        "planned": {"sets": 4, "reps": 4, "added_kg": 22.5},
                        "sets": [],
                    },
                ],
            },
            {
                "id": "day3",
                "title": "量日",
                "exercises": [
                    {
                        "id": "weighted_pullup",
                        "name_zh": "負重引體",
                        "planned": {"sets": 2, "reps": 6, "added_kg": 17.5},
                    },
                ],
            },
        ],
    }
    (user_dir / "board.yaml").write_text(
        yaml.dump(board, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


def test_list_open_day_expands_planned_and_sets_active_day_id(tmp_path, capsys):
    ud = tmp_path / "user"
    _fixture_list_board(ud)
    main(["open-day", "--user-dir", str(ud), "--day", "day1"])
    out = capsys.readouterr().out
    assert "負重引體" in out
    assert "4×4＠+22.5" in out
    board = yaml.safe_load((ud / "board.yaml").read_text(encoding="utf-8"))
    assert board["active_day"] == "day1"
    assert isinstance(board["days"], list)
    ex = board["days"][0]["exercises"][0]
    assert len(ex["sets"]) == 4
    assert ex["sets"][0].get("mark", "wait") == "wait"


def test_list_skip_day_keeps_logged_set_marks(tmp_path):
    ud = tmp_path / "user"
    _fixture_list_board(ud)
    board = yaml.safe_load((ud / "board.yaml").read_text(encoding="utf-8"))
    board["days"][0]["exercises"][0]["sets"] = [
        {"n": 1, "reps": 4, "added_kg": 22.5, "rpe": 8, "mark": "ok"},
    ]
    (ud / "board.yaml").write_text(
        yaml.dump(board, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    main(["open-day", "--user-dir", str(ud), "--day", "day1"])
    main(
        [
            "skip-day",
            "--user-dir",
            str(ud),
            "--day",
            "day1",
            "--reason",
            "趕時間",
            "--at",
            "2026-09-26",
        ]
    )
    board = yaml.safe_load((ud / "board.yaml").read_text(encoding="utf-8"))
    sets = board["days"][0]["exercises"][0]["sets"]
    assert sets[0]["mark"] == "ok"
    assert sets[1]["mark"] == "skip"
    assert board["active_day"] is None


def test_list_volume_tallies_planned_from_microcycle(tmp_path):
    ud = tmp_path / "user"
    _fixture_list_board(ud)
    board = yaml.safe_load((ud / "board.yaml").read_text(encoding="utf-8"))
    done, weekly = tally_from_board(board)
    assert weekly.get("背闊") == 4.0 + 2.0
    assert done.get("背闊", 0) == 0.0
