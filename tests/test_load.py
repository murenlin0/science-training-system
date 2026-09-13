"""類型 P / B / I。通用數字鎖算術，不是某人的 1RM。"""

import pytest

from core.assertions import (
    assert_backoff_same_definition,
    assert_karvonen_identity,
    assert_type_b_pct_on_system_load,
    assert_type_p_ignores_bodyweight,
)
from core.classify import (
    MovementType,
    by_type,
    get,
    ladder_factor,
    next_variant,
    register_from_dict,
)
from core.e1rm import bodyweight_1rm_added
from core.karvonen import karvonen
from core.load import (
    build_warmup,
    compute_load,
    isometric_volume,
    normalize_increment,
)

BW = 100.0
WPU_1RM_ADDED = 50.0
WPU_TOTAL_1RM = BW + WPU_1RM_ADDED  # 150
OHP_1RM = 50.0


def test_primaries_are_declarable_not_hardcoded():
    assert get("ohp").mtype == MovementType.PURE
    assert get("weighted_pullup").mtype == MovementType.BODYWEIGHT
    assert get("planche").mtype == MovementType.ISOMETRIC


def test_deadlift_cap_is_data_not_constant():
    assert get("deadlift").weekly_cap == 6
    assert get("deadlift").min_gap_hours == 72
    assert get("ohp").weekly_cap is None


def test_primaries_forbid_failure_accessories_allow():
    assert get("planche").allow_failure is False
    assert get("weighted_pullup").allow_failure is False
    assert get("lateral_raise").allow_failure is True


def test_unknown_movement_gives_actionable_error():
    with pytest.raises(KeyError, match="不在註冊表中"):
        get("air_flare")


def test_custom_movement_registration():
    mv = register_from_dict({
        "key": "ring_muscle_up", "name_zh": "吊環暴力上槓",
        "name_en": "Ring Muscle-up", "type": "B", "mev": 4, "mrv": 12,
    })
    assert mv.mtype == MovementType.BODYWEIGHT
    assert get("ring_muscle_up").name_en == "Ring Muscle-up"


def test_custom_movement_rejects_bad_type():
    with pytest.raises(ValueError, match="type"):
        register_from_dict({
            "key": "bogus", "name_zh": "假動作",
            "name_en": "Bogus", "type": "X",
        })


def test_every_movement_has_both_names():
    for mv in list(by_type(MovementType.PURE)
                   + by_type(MovementType.BODYWEIGHT)
                   + by_type(MovementType.ISOMETRIC)):
        assert mv.name_zh and mv.name_en, f"{mv.key} 缺少中文或英文名稱"


def test_type_p_ignores_bodyweight():
    p = compute_load("ohp", 70.0, one_rm=OHP_1RM)
    assert p.external_weight == 35.0
    assert p.total_load is None
    assert p.bodyweight is None
    assert_type_p_ignores_bodyweight("ohp", 70.0, OHP_1RM)


def test_type_b_percentage_applies_to_total_system_load():
    p = compute_load("weighted_pullup", 70.0,
                     one_rm_added=WPU_1RM_ADDED, bodyweight=BW)
    assert p.added_weight == 5.0
    assert p.total_load == 105.0
    assert_type_b_pct_on_system_load("weighted_pullup", 70.0, WPU_1RM_ADDED, BW)


def test_type_b_accepts_system_1rm_L():
    p = compute_load("weighted_pullup", 70.0, system_1rm_L=150.0, bodyweight=BW)
    assert p.added_weight == 5.0
    assert p.total_load == 105.0


def test_type_b_rejects_one_rm_name():
    with pytest.raises(ValueError, match="one_rm_added"):
        compute_load("weighted_pullup", 70.0, one_rm=WPU_1RM_ADDED, bodyweight=BW)


def test_type_b_naive_percentage_would_be_dangerous():
    correct = compute_load("weighted_pullup", 70.0,
                           one_rm_added=WPU_1RM_ADDED, bodyweight=BW)
    naive_added = WPU_1RM_ADDED * 0.70
    naive_total = BW + naive_added
    naive_intensity = naive_total / WPU_TOTAL_1RM
    assert naive_intensity > 0.85
    assert correct.total_load / WPU_TOTAL_1RM == pytest.approx(0.70, abs=0.01)
    assert naive_added - correct.added_weight > 15


def test_type_b_warmup_ladder_all_steps_on_total_load():
    warmup = build_warmup("weighted_pullup",
                          one_rm_added=WPU_1RM_ADDED, bodyweight=BW)
    assert len(warmup) == 4
    assert warmup[0].added_weight == 0.0
    assert warmup[0].total_load == BW
    intensities = [w.total_load / WPU_TOTAL_1RM for w in warmup]
    assert intensities == sorted(intensities)
    for w, expected in zip(warmup[1:], (0.70, 0.80, 0.90)):
        assert w.total_load / WPU_TOTAL_1RM == pytest.approx(expected, abs=0.015)
    assert warmup[-1].added_weight < WPU_1RM_ADDED


def test_type_b_below_bodyweight_flags_assistance():
    p = compute_load("pullup", 50.0, one_rm_added=WPU_1RM_ADDED, bodyweight=BW)
    assert p.added_weight < 0
    assert "減重" in p.warning


def test_type_b_requires_bodyweight():
    with pytest.raises(ValueError, match="bodyweight"):
        compute_load("weighted_pullup", 70.0, one_rm_added=WPU_1RM_ADDED)


def test_bodyweight_epley_returns_added_not_total():
    assert bodyweight_1rm_added(BW, 50.0, reps=1) == pytest.approx(50.0)
    est = bodyweight_1rm_added(BW, 50.0, reps=2)
    assert est == pytest.approx(60.0, abs=0.1)


def test_type_i_prescribes_half_max_hold():
    p = compute_load("planche", 50.0, max_hold_s=12)
    assert p.hold_seconds == 6.0
    assert p.warning is None


def test_type_i_warns_over_work_cap():
    p = compute_load("planche", 80.0, max_hold_s=12)
    assert "70%" in p.warning


def test_type_i_sixty_five_is_working_set():
    p = compute_load("planche", 65.0, max_hold_s=12)
    assert p.hold_seconds == 7.8
    assert p.warning is None


def test_isometric_ladder_and_progression():
    assert ladder_factor("planche", "tuck_planche") == 0.40
    assert ladder_factor("planche", "straddle_planche") == 0.80
    nxt = next_variant("planche", "adv_tuck_planche")
    assert nxt[0] == "straddle_planche"
    assert next_variant("planche", "full_planche") is None


def test_isometric_volume_scales_with_difficulty():
    tuck = isometric_volume("tuck_planche", "planche", 60)
    straddle = isometric_volume("straddle_planche", "planche", 60)
    assert straddle > tuck
    assert tuck == 24.0


def test_type_i_rejects_weight_increment():
    with pytest.raises(ValueError, match="等長"):
        normalize_increment("planche", current_load=10)


def test_fixed_increment_flagged_on_small_lift():
    r = normalize_increment("ohp", current_load=OHP_1RM, requested_increment=2.5)
    assert r["exceeds_cap"] is True
    assert r["requested_pct"] == pytest.approx(5.0, abs=0.1)
    assert r["recommended_increment"] == 1.25
    assert r["recommended_pct"] <= 2.5


def test_same_increment_fine_on_large_lift():
    r = normalize_increment("squat", current_load=150.0, requested_increment=2.5)
    assert r["exceeds_cap"] is False


def test_type_b_increment_denominator_is_system_load():
    r = normalize_increment("weighted_pullup", current_load=50.0, bodyweight=BW)
    assert r["system_load"] == 150.0
    assert r["cap_kg"] == pytest.approx(3.75, abs=0.01)


def test_describe_includes_both_names_and_total_load():
    p = compute_load("weighted_pullup", 90.0, one_rm_added=WPU_1RM_ADDED,
                     bodyweight=BW, reps=1, sets=1, label="Top Set")
    text = p.describe()
    assert "負重引體向上" in text and "Weighted Pull-up" in text
    assert "總負荷" in text


def test_karvonen_and_backoff_identities():
    assert karvonen(190, 60, 60) == (190 - 60) * 0.60 + 60
    assert_karvonen_identity(190, 60, 60)
    assert_backoff_same_definition(50.0, 12)
