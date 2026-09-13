"""L0 斷言：算錯就炸，不靠散文。"""

from __future__ import annotations

from core.classify import MovementType, get
from core.karvonen import karvonen
from core.load import backoff_load, compute_load


def assert_type_b_pct_on_system_load(
    movement: str,
    pct: float,
    one_rm_added: float,
    bodyweight: float,
) -> None:
    p = compute_load(movement, pct, one_rm_added=one_rm_added, bodyweight=bodyweight)
    target_l = (bodyweight + one_rm_added) * (pct / 100.0)
    assert p.mtype == MovementType.BODYWEIGHT.value
    assert abs((p.total_load or 0) - (bodyweight + (p.added_weight or 0))) < 0.02
    naive = one_rm_added * (pct / 100.0)
    assert abs((p.added_weight or 0) - naive) > 1, "若接近 naive，代表百分比打在掛重上"
    assert abs((bodyweight + (p.added_weight or 0)) - target_l) < 2.6  # 片重步進


def assert_type_p_ignores_bodyweight(movement: str, pct: float, one_rm: float) -> None:
    p = compute_load(movement, pct, one_rm=one_rm, bodyweight=999)
    assert p.bodyweight is None
    assert p.external_weight is not None


def assert_primary_not_listed_as_accessory(
    primaries: list[str], chosen: list[str]
) -> None:
    from core.assistance import forbidden_as_accessory
    ban = forbidden_as_accessory(primaries)
    hit = set(chosen) & ban
    assert not hit, f"已宣告主項不得再當輔助：{sorted(hit)}"


def assert_karvonen_identity(hr_max: float, hr_rest: float, pct: float) -> None:
    got = karvonen(hr_max, hr_rest, pct)
    expect = (hr_max - hr_rest) * (pct / 100.0) + hr_rest
    assert got == expect


def assert_backoff_same_definition(top: float, discount_pct: float) -> None:
    assert backoff_load(top, discount_pct) == top * (1 - discount_pct / 100.0)


def assert_failure_policy(movement: str, is_primary: bool) -> None:
    mv = get(movement)
    if is_primary:
        assert mv.allow_failure is False, f"主項 {movement} 不允許力竭"
