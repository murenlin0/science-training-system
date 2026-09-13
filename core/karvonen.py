"""Karvonen：THR = (HRmax − HRrest) × % + HRrest。HRmax 禁止用 220−年齡。"""

HRR_ZONES = {
    "very_light": (20, 30),
    "light": (30, 39),
    "moderate": (40, 59),
    "vigorous": (60, 89),
    "near_max": (90, 100),
}


def karvonen(hr_max: float, hr_rest: float, pct: float) -> float:
    if hr_max <= hr_rest:
        raise ValueError("HRmax 必須大於 HRrest")
    return (hr_max - hr_rest) * (pct / 100.0) + hr_rest


def zone_thr(hr_max: float, hr_rest: float, zone: str) -> tuple[float, float]:
    if zone not in HRR_ZONES:
        raise KeyError(f"未知 HRR 區：{zone}。可用：{sorted(HRR_ZONES)}")
    lo, hi = HRR_ZONES[zone]
    return karvonen(hr_max, hr_rest, lo), karvonen(hr_max, hr_rest, hi)
