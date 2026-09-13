"""處方負荷。P 用外載 1RM；B 百分比只打在 L；I 用秒。"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Optional

from core.classify import ISOMETRIC_WORK_PCT_CAP, MovementType, get, ladder_factor


def round_weight(weight: float, plate_step: float = 2.5) -> float:
    return (weight // plate_step) * plate_step


@dataclass
class LoadPrescription:
    movement: str
    mtype: str
    pct: Optional[float] = None
    external_weight: Optional[float] = None
    added_weight: Optional[float] = None
    total_load: Optional[float] = None
    bodyweight: Optional[float] = None
    hold_seconds: Optional[float] = None
    reps: Optional[int] = None
    sets: Optional[int] = None
    rpe: Optional[float] = None
    label: str = ""
    warning: Optional[str] = None

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}

    def describe(self) -> str:
        mv = get(self.movement)
        name = f"{mv.name_zh}（{mv.name_en}）"
        if self.mtype == MovementType.ISOMETRIC.value:
            body = f"{self.hold_seconds:g} 秒"
        elif self.mtype == MovementType.BODYWEIGHT.value:
            sign = "+" if self.added_weight >= 0 else "−"
            body = f"掛重 {sign}{abs(self.added_weight):g}kg（總負荷 {self.total_load:g}kg）"
        else:
            body = f"{self.external_weight:g}kg"
        extra = []
        if self.sets and self.reps:
            extra.append(f"{self.sets}組 × {self.reps}下")
        elif self.reps:
            extra.append(f"{self.reps}下")
        if self.rpe is not None:
            extra.append(f"RPE {self.rpe:g}")
        if self.pct is not None:
            extra.append(f"[{self.pct:g}%]")
        line = " ｜ ".join([name, body, *extra])
        return f"{self.label}：{line}" if self.label else line


def _added_1rm(*, name: str, one_rm, one_rm_added, system_1rm_L, bodyweight: float) -> float:
    if one_rm is not None:
        raise ValueError(f"{name}（類型 B）請傳 one_rm_added（掛重 1RM）或 system_1rm_L，不要用 one_rm")
    if system_1rm_L is not None and one_rm_added is not None:
        raise ValueError(f"{name}：one_rm_added 與 system_1rm_L 只能傳一個")
    if system_1rm_L is not None:
        if system_1rm_L <= bodyweight:
            raise ValueError(f"system_1rm_L ({system_1rm_L:g}) 必須大於體重 {bodyweight:g}")
        return system_1rm_L - bodyweight
    if one_rm_added is None:
        raise ValueError(f"{name}（類型 B）需要 one_rm_added 或 system_1rm_L")
    return float(one_rm_added)


def compute_load(
    movement: str,
    pct: float,
    one_rm: Optional[float] = None,
    one_rm_added: Optional[float] = None,
    system_1rm_L: Optional[float] = None,
    bodyweight: Optional[float] = None,
    max_hold_s: Optional[float] = None,
    reps: Optional[int] = None,
    sets: Optional[int] = None,
    rpe: Optional[float] = None,
    plate_step: float = 2.5,
    label: str = "",
) -> LoadPrescription:
    mv = get(movement)
    t = mv.mtype
    if t == MovementType.ISOMETRIC:
        if max_hold_s is None:
            raise ValueError(f"{mv.name_zh}（類型 I）需要 max_hold_s")
        hold = round(max_hold_s * pct / 100.0, 1)
        warn = None
        if pct > ISOMETRIC_WORK_PCT_CAP and not mv.allow_failure:
            warn = (
                f"{mv.name_zh} 處方 {pct:g}% 超過 {ISOMETRIC_WORK_PCT_CAP:g}% 工作組上限。"
                f"等長工作組用 60–70% 最大秒數；撐到力竭仍禁。"
            )
        return LoadPrescription(
            movement=mv.key, mtype=t.value, pct=pct,
            hold_seconds=hold, sets=sets, label=label, warning=warn,
        )
    if t == MovementType.PURE:
        if one_rm is None:
            raise ValueError(f"{mv.name_zh}（類型 P）需要 one_rm（外載）")
        if one_rm_added is not None or system_1rm_L is not None:
            raise ValueError(f"{mv.name_zh}（類型 P）只用 one_rm，不要傳掛重或 L")
        return LoadPrescription(
            movement=mv.key, mtype=t.value, pct=pct,
            external_weight=round_weight(one_rm * pct / 100.0, plate_step),
            reps=reps, sets=sets, rpe=rpe, label=label,
        )
    if bodyweight is None:
        raise ValueError(f"{mv.name_zh}（類型 B）需要 bodyweight，否則算不了 L")
    added_1rm = _added_1rm(
        name=mv.name_zh, one_rm=one_rm, one_rm_added=one_rm_added,
        system_1rm_L=system_1rm_L, bodyweight=bodyweight,
    )
    target_l = (bodyweight + added_1rm) * pct / 100.0
    raw_added = target_l - bodyweight
    added = round_weight(raw_added, plate_step)
    warn = None
    if raw_added < 0:
        warn = (
            f"目標總負荷 {target_l:.1f}kg 低於體重 {bodyweight:g}kg，"
            f"需減重 {abs(added):g}kg（彈力帶／輔助引體機），不是掛重。"
        )
    elif raw_added < plate_step / 2:
        warn = f"掛重趨近 0，實務上做徒手即可（原始值 {raw_added:.1f}kg）"
    return LoadPrescription(
        movement=mv.key, mtype=t.value, pct=pct,
        added_weight=added, total_load=round(bodyweight + added, 2),
        bodyweight=bodyweight, reps=reps, sets=sets, rpe=rpe,
        label=label, warning=warn,
    )


_P_WARMUP = ((50.0, 5, "熱身 1"), (70.0, 3, "熱身 2"), (85.0, 1, "熱身 3"))
_B_WARMUP = ((70.0, 3, "熱身 2"), (80.0, 2, "熱身 3"), (90.0, 1, "熱身 4"))


def build_warmup(
    movement: str,
    one_rm: Optional[float] = None,
    one_rm_added: Optional[float] = None,
    system_1rm_L: Optional[float] = None,
    bodyweight: Optional[float] = None,
    max_hold_s: Optional[float] = None,
    ladder: Optional[list] = None,
    plate_step: float = 2.5,
) -> list:
    mv = get(movement)
    kw = dict(plate_step=plate_step, one_rm=one_rm, one_rm_added=one_rm_added,
              system_1rm_L=system_1rm_L, bodyweight=bodyweight, max_hold_s=max_hold_s)
    if mv.mtype == MovementType.ISOMETRIC:
        return [compute_load(movement, 40.0, sets=1, label="等長熱身", **kw)]
    if mv.mtype == MovementType.BODYWEIGHT:
        first = LoadPrescription(
            movement=mv.key, mtype=mv.mtype.value,
            added_weight=0.0, total_load=bodyweight, bodyweight=bodyweight,
            reps=5, sets=1, label="熱身 1（徒手）",
        )
        steps = ladder or _B_WARMUP
        return [first] + [
            compute_load(movement, pct, reps=reps, sets=1, label=lbl, **kw)
            for pct, reps, lbl in steps
        ]
    steps = ladder or _P_WARMUP
    return [
        compute_load(movement, pct, reps=reps, sets=1, label=lbl, **kw)
        for pct, reps, lbl in steps
    ]


def normalize_increment(
    movement: str,
    current_load: float,
    bodyweight: Optional[float] = None,
    requested_increment: Optional[float] = None,
    micro_plate: float = 1.25,
) -> dict:
    mv = get(movement)
    if mv.mtype == MovementType.ISOMETRIC:
        raise ValueError(f"{mv.name_zh} 是等長動作，進階靠秒數與難度階梯，不用重量增量。")
    system = current_load
    if mv.mtype == MovementType.BODYWEIGHT:
        if bodyweight is None:
            raise ValueError(f"{mv.name_zh}（類型 B）需要 bodyweight 才能算系統負荷")
        system = bodyweight + current_load
    cap = system * (mv.increment_pct_cap / 100.0)
    rec = max(1, int(cap / micro_plate)) * micro_plate
    out = {
        "movement": mv.key,
        "system_load": round(system, 2),
        "cap_pct": mv.increment_pct_cap,
        "cap_kg": round(cap, 2),
        "recommended_increment": rec,
        "recommended_pct": round(rec / system * 100, 2),
        "micro_plate": micro_plate,
    }
    if requested_increment is None:
        return out
    req_pct = requested_increment / system * 100
    out["requested_increment"] = requested_increment
    out["requested_pct"] = round(req_pct, 2)
    out["exceeds_cap"] = req_pct > mv.increment_pct_cap
    if out["exceeds_cap"]:
        out["warning"] = (
            f"+{requested_increment:g}kg 佔系統負荷 {req_pct:.1f}%，"
            f"超過 {mv.increment_pct_cap:g}% 上限。"
            f"改用 {rec:g}kg（{out['recommended_pct']:.1f}%）。"
        )
    return out


def backoff_load(top_load: float, discount_pct: float) -> float:
    return top_load * (1 - discount_pct / 100.0)


def isometric_volume(variant_key: str, ladder_name: str, total_seconds: float) -> float:
    return round(total_seconds * ladder_factor(ladder_name, variant_key), 2)
