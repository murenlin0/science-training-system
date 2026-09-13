"""主項 → 輔助查表。這是舊系統沒有的 keyed lookup。"""

from pathlib import Path

import pytest
import yaml

from core.assertions import assert_failure_policy, assert_primary_not_listed_as_accessory
from core.assistance import (
    assert_every_registrable_primary_has_map,
    for_primary,
    for_primaries,
    forbidden_as_accessory,
)
from core.classify import primaries

ROOT = Path(__file__).resolve().parents[1]


def test_every_primary_has_assistance_map():
    assert_every_registrable_primary_has_map()
    assert {m.key for m in primaries()} <= set(for_primaries([m.key for m in primaries()]))


def test_ohp_forbids_ohp_and_keeps_useful_list():
    row = for_primary("ohp")
    assert "ohp" in row["forbid_as_accessory"]
    ids = {x["id"] for x in row["supplemental"] + row["accessory"]}
    assert {"push_press", "face_pull", "leaning_cable_lateral"} <= ids
    assert "ohp" not in ids


def test_weighted_pullup_forbids_both_vertical_pulls():
    ban = forbidden_as_accessory(["weighted_pullup"])
    assert ban == {"weighted_pullup", "pullup"}
    row = for_primary("weighted_pullup")
    ids = {x["id"] for x in row["supplemental"] + row["accessory"]}
    assert "barbell_row" in ids
    assert "weighted_pullup" not in ids
    assert "pullup" not in ids


def test_planche_is_not_in_the_old_big_db_but_is_keyed_here():
    row = for_primary("planche")
    ids = {x["id"] for x in row["supplemental"] + row["accessory"]}
    assert {"planche_lean", "scapular_pushup", "wrist_prep"} <= ids


def test_lookup_only_selected_primaries():
    got = for_primaries(["ohp", "planche"])
    assert set(got) == {"ohp", "planche"}
    with pytest.raises(KeyError, match="沒有輔助對照表"):
        for_primary("lateral_raise")


def test_primary_cannot_be_relisted():
    assert_primary_not_listed_as_accessory(["ohp"], ["face_pull", "z_press"])
    with pytest.raises(AssertionError, match="不得再當輔助"):
        assert_primary_not_listed_as_accessory(["ohp"], ["ohp", "face_pull"])


def test_failure_policy_on_primaries():
    for m in primaries():
        assert_failure_policy(m.key, is_primary=True)


def test_literature_files_exist():
    data = yaml.safe_load((ROOT / "config" / "assistance.yaml").read_text(encoding="utf-8"))
    for key, row in data["primaries"].items():
        path = ROOT / row["literature"]
        assert path.is_file(), f"{key} 缺文獻檔 {path}"
        text = path.read_text(encoding="utf-8")
        assert "rule_ids" in text and "citation_ids" in text


VALID_SUPPORT = {"principle", "class", "exercise", "coach", "biomech"}
GRADE_OK = {
    "principle": {"C"},
    "coach": {"C"},
    "class": {"B", "C"},
    "biomech": {"B", "C"},
    "exercise": {"A", "B", "C"},
}


def test_every_assistance_item_has_honest_support():
    """有 citation_ids ≠ 該動作有 RCT。grade 不得高於 support。"""
    data = yaml.safe_load((ROOT / "config" / "assistance.yaml").read_text(encoding="utf-8"))
    cites = {
        c["id"]: c["grade"]
        for c in yaml.safe_load((ROOT / "evidence" / "citations.yaml").read_text(encoding="utf-8"))["citations"]
    }
    for primary, row in data["primaries"].items():
        for item in row["supplemental"] + row["accessory"]:
            loc = f"{primary}/{item['id']}"
            assert item.get("citation_ids"), f"{loc} 缺 citation_ids"
            assert item.get("support") in VALID_SUPPORT, f"{loc} support 無效"
            assert item.get("grade") in {"A", "B", "C"}, f"{loc} grade 無效"
            assert item["grade"] in GRADE_OK[item["support"]], f"{loc} grade {item['grade']} 高於 support={item['support']}"
            if item["grade"] == "A":
                assert item["support"] == "exercise", f"{loc} 不得用原則把點名抬成 A"
                assert any(cites[cid] == "A" for cid in item["citation_ids"]), f"{loc} grade A 但沒有 A 級引用"
            for cid in item["citation_ids"]:
                assert cid in cites, f"{loc} 未登記 {cid}"


def test_planche_menu_covers_limiters_and_emg():
    row = for_primary("planche")
    ids = {x["id"] for x in row["supplemental"] + row["accessory"]}
    assert {
        "planche_lean", "scapular_pushup", "straight_arm_support",
        "feet_supported_planche", "straight_arm_front_raise",
        "wrist_prep", "l_sit", "hip_openers",
    } <= ids
    assert "wang_shan2023" in row["citation_ids"]
    assert "rosaci2025" in row["citation_ids"]
    raise_ids = {x["id"]: x for x in row["supplemental"]}
    assert raise_ids["straight_arm_front_raise"]["support"] == "exercise"
    assert raise_ids["planche_lean"]["support"] == "biomech"
