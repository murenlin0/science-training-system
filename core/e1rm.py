"""估 1RM。B 先合成 L 再減體重。有 RPE 用表，沒有才 Epley。"""

from __future__ import annotations

# 次數×RPE → %1RM。缺格取同次數最近 RPE。
_RPE = {
    (1, 10): 100, (2, 10): 95, (3, 10): 92, (4, 10): 90, (5, 10): 87,
    (1, 9.5): 97, (2, 9.5): 92, (3, 9.5): 89, (4, 9.5): 87, (5, 9.5): 84,
    (1, 9): 95, (2, 9): 90, (3, 9): 87, (4, 9): 85, (5, 9): 82,
    (1, 8.5): 93, (2, 8.5): 88, (3, 8.5): 85, (4, 8.5): 82, (5, 8.5): 79,
    (1, 8): 90, (2, 8): 85, (3, 8): 82, (4, 8): 80, (5, 8): 77,
    (1, 7.5): 88, (2, 7.5): 83, (3, 7.5): 80, (4, 7.5): 77, (5, 7.5): 74,
    (1, 7): 85, (2, 7): 80, (3, 7): 77, (4, 7): 75, (5, 7): 72,
}


def epley_1rm(load: float, reps: int) -> float:
    if reps < 1:
        raise ValueError(f"reps 須 ≥1，收到 {reps}")
    return float(load) if reps == 1 else float(load) * (1 + reps / 30.0)


def bodyweight_1rm_added(bodyweight: float, added: float, reps: int) -> float:
    return epley_1rm(bodyweight + added, reps) - bodyweight


def rpe_to_percentage(reps: int, rpe: float) -> float:
    if (reps, rpe) in _RPE:
        return _RPE[(reps, rpe)]
    nearby = [k[1] for k in _RPE if k[0] == reps]
    if not nearby:
        return 80.0
    closest = min(nearby, key=lambda x: abs(x - rpe))
    return _RPE[(reps, closest)]


def e1rm_from_rpe(weight: float, reps: int, rpe: float) -> float:
    return weight / (rpe_to_percentage(reps, rpe) / 100.0)


def e1rm_added_from_rpe(bodyweight: float, added: float, reps: int, rpe: float) -> float:
    return e1rm_from_rpe(bodyweight + added, reps, rpe) - bodyweight
