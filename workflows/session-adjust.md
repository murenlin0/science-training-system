---
skill: science-training-system
category: session
description: 正在練。只改今天剩下的。每組立刻寫紀錄並貼表。
---

# 當日

觸發：開練、回報組、問下一組。重排整週 → `design-plan.md`。容量太大 → `modify-plan.md`。
紀錄格式 → `logging.md`。算表 → `core/session_log.py`、`core/volume.py`。

## 開練（一次）

對齊今天幾號動作。對方說用存檔才讀 `user/session.yaml`／`user/plan.md`。不要預設主項。
類型 I 沒有 `max_hold_s` → 今天只測，不開假工作組。
熱身與下一組重量走 `core/load.py`。類型 B 用 `one_rm_added` 或 `system_1rm_L`，禁止手算。

若離本週 Day 1 已約一週、後面幾練還沒做：先問要開下一週（沒跑的留空）還是先跑完。不要自己用日曆切週。

| 類型 | 必報 |
|------|------|
| P | 動作、組序、槓重、次數、RPE |
| B | 同上，**掛重**（或 L） |
| I | 動作／難度、秒、RPE |

## 每組

1. 立刻寫入 `user/session.yaml`，再渲 `user/session.html`。聊天**直接貼**更新後的紀錄區（見 `logging.md`）。不要等點頭、不要靠附件。
2. 先答夾問，再出下一組。尖銳痛／卡住／胸痛：該動作今天停。
3. Δ = 實際 RPE − 目標 RPE。沒做滿視同 Δ ≥ +1。技術崩也當偏高。

| Δ | 今天剩下的 |
|---|----------------|
| ≤ −1.5 | 可加最小片（B 仍算 L；I 加秒或維持難度）。技術不乾淨不加。 |
| −0.5～+0.5 | 照計畫 |
| +1～+1.5 | 維持或略降；不追加組 |
| ≥ +2 | 砍剩餘 back-off 1 組（不要另列 BO 動作名） |
| 沒做滿 | 下一組降負荷，不磨失敗組 |

類型 I 工作組鎖 60–70% max-hold。超過 `ISOMETRIC_WORK_PCT_CAP` 截斷。
組中不改 e1RM／TM。探測組折抵當天原訂工作組，測完不要再強迫做滿。

## 收工

今日摘要用同一份紀錄區，不要再問「可不可以寫 log」。
只有 Δ ≥ +2 或連續兩課超標，才提後面 1–2 個變數（細節走 `modify-plan.md`）。
回覆末附 Volume（header + 全部肌群）。
