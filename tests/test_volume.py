"""Volume 燈號與當日表。landmarks 不當門。"""

from core.session_log import format_day, format_lift, tally_week
from core.volume import add_sets, band, format_landmarks, weights_for


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
