"""Volume 燈號與當日表。landmarks 不當門。"""

from pathlib import Path

import yaml

from core.session_log import format_day, format_lift, tally_week
from core.volume import add_sets, band, format_landmarks, reset_cache, weights_for

ROOT = Path(__file__).resolve().parents[1]


def test_planche_weights_match_brief():
    assert weights_for("planche") == [("前三角", 1.0), ("二頭", 0.5)]


def test_fractional_stack():
    done = {}
    add_sets(done, "planche", 3)
    add_sets(done, "ohp", 3)
    assert done["前三角"] == 6.0
    assert done["二頭"] == 1.5
    assert done["三頭"] == 1.5


def test_zero_is_below_and_listed():
    text = format_landmarks({}, {})
    assert text.startswith("肌肥大地板")
    assert "不當擋門" in text.splitlines()[1]
    assert "背闊" in text and "0/0⚪" in text
    assert band("背闊", 0) == "below"


def test_zero_weekly_below_even_when_mev_floor_is_zero():
    assert band("臀", 0) == "below"
    assert band("腹", 0) == "below"


def test_new_movement_weights_load():
    assert weights_for("barbell_row") == [("上背", 1.0), ("後三角", 0.5), ("二頭", 0.3)]
    assert weights_for("planche_lean") == [("前三角", 1.0), ("二頭", 0.5)]


def _seed_volume_config(base: Path) -> None:
    cfg = base / "config"
    cfg.mkdir(parents=True)
    (cfg / "volume_landmarks.yaml").write_text(
        (ROOT / "config" / "volume_landmarks.yaml").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (cfg / "volume_weights.yaml").write_text(
        (ROOT / "config" / "volume_weights.yaml").read_text(encoding="utf-8"),
        encoding="utf-8",
    )


def test_user_weights_overlay_when_valid(tmp_path, monkeypatch):
    _seed_volume_config(tmp_path)
    user_dir = tmp_path / "user"
    user_dir.mkdir()
    (user_dir / "volume_weights.yaml").write_text(
        yaml.dump({"movements": {"custom_only": [{"m": "胸", "w": 1.0}]}}, allow_unicode=True),
        encoding="utf-8",
    )
    monkeypatch.setattr("core.volume._DIR", tmp_path)
    reset_cache()
    try:
        assert weights_for("custom_only") == [("胸", 1.0)]
        assert weights_for("ohp") == []
    finally:
        reset_cache()
        monkeypatch.setattr("core.volume._DIR", ROOT)


def test_user_weights_invalid_overlay_falls_back_to_config(tmp_path, monkeypatch):
    _seed_volume_config(tmp_path)
    user_dir = tmp_path / "user"
    user_dir.mkdir()
    (user_dir / "volume_weights.yaml").write_text("default_direct: 1.0\n", encoding="utf-8")
    monkeypatch.setattr("core.volume._DIR", tmp_path)
    reset_cache()
    try:
        assert weights_for("ohp") == [("前三角", 1.0), ("三頭", 0.5)]
    finally:
        reset_cache()
        monkeypatch.setattr("core.volume._DIR", ROOT)


def test_six_front_delt_is_mev_green():
    assert band("前三角", 6.0) == "mev"
    text = format_landmarks({"前三角": 6.0}, {"前三角": 6.0})
    assert "6/6🟢" in text


def test_over_mrv_is_red():
    assert band("前三角", 20) == "over"


def test_sort_puts_heavier_relative_first():
    text = format_landmarks({"前三角": 6, "背闊": 0}, {"前三角": 6, "背闊": 0})
    line = text.splitlines()[-1]
    assert line.index("前三角") < line.index("背闊")


def test_lift_table_one_row_per_set_no_bo_title():
    block = format_lift({
        "key": "weighted_pullup",
        "name": "負重引體向上",
        "sets": [
            {"goal": "+12.5×5 @8", "done": "+12.5×5 @8", "mark": "ok"},
            {"goal": "+10×5 @7", "done": None, "mark": "wait"},
        ],
    }, highlight=0)
    assert "**負重引體向上**" in block
    assert "背闊1" in block and "二頭0.5" in block
    assert "BO" not in block
    assert block.count("| +") == 2


def test_tally_counts_planned_and_done():
    data = {
        "days": [{
            "n": 1,
            "lifts": [{
                "key": "ohp",
                "sets": [
                    {"mark": "ok"},
                    {"mark": "wait"},
                ],
            }],
        }],
    }
    done, week = tally_week(data)
    assert week["前三角"] == 2.0
    assert done["前三角"] == 1.0


def test_format_day_includes_volume_header():
    data = {
        "week_label": "第1周",
        "days": [{"n": 1, "lifts": [{"key": "ohp", "name": "肩推", "sets": [{"goal": "x", "mark": "ok"}]}]}],
    }
    text = format_day(data, 1, just=("ohp", 0))
    assert "肌肥大地板" in text
    assert "肩推" in text


def test_html_roundtrip_keeps_sets(tmp_path):
    from core.session_log import load_session, parse_session, render_session, save_session

    data = {
        "week_label": "第1周",
        "opened_on": "2026-09-13",
        "days": [{
            "n": 1,
            "lifts": [{
                "key": "ohp",
                "name": "肩推",
                "sets": [
                    {"goal": "35×5 @8", "done": "35×5 @8", "mark": "ok"},
                    {"goal": "32.5×5 @7", "done": None, "mark": "wait"},
                ],
                "last_week": ["30×5", None],
            }],
        }],
    }
    back = parse_session(render_session(data))
    lift = back["days"][0]["lifts"][0]
    assert back["week_label"] == "第1周"
    assert back["opened_on"] == "2026-09-13"
    assert lift["sets"][0] == {"goal": "35×5 @8", "done": "35×5 @8", "mark": "ok"}
    assert lift["sets"][1]["done"] is None
    assert lift["last_week"][0] == "30×5"
    html_p = tmp_path / "session.html"
    save_session(html_p, data)
    assert load_session(html_p)["days"][0]["lifts"][0]["key"] == "ohp"


def test_yaml_only_still_loads(tmp_path):
    from core.session_log import load_session

    p = tmp_path / "session.yaml"
    p.write_text("week_label: 舊檔\ndays:\n- n: 1\n  lifts: []\n", encoding="utf-8")
    assert load_session(p)["week_label"] == "舊檔"
