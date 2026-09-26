---
skill: science-training-system
category: session
description: 當日紀錄格式與 Volume 頁腳。真源是 HTML，聊天只是渲染。
---

# 紀錄

真源：`user/session.html`（gitignore）。課表計畫真源：`user/board.yaml`。

**開練／跳過日／回報組：先跑** `python -m core.session_cli`（見 `session-adjust.md`），把 CLI 印出的 markdown **原樣貼進聊天**，再在 prose 補下一組數字與 Δ 調整。不要從對話回推組數或重量。還沒有 html 時，才讀一次舊的 `user/session.yaml`。

## 聊天順序（訓練中強制）

**每次回報組／開練／換動作，都要貼「今天整份課表」的紀錄表**，不要只貼當下那一個動作。

整表動作順序（上→下）：

1. **已做完的動作**（課表時間序；剛完成的可加粗）
2. **正在做／下一組所屬動作**
3. **還沒做的動作**

每個動作一張小表，欄位固定左→右：

`目標 | 這次 | 上次 DayX`

| 欄 | 寫什麼 |
|----|--------|
| 目標 | 今日計畫：組×次／秒＠負荷＋RPE（含 BO 寫在同一格，勿另開 BO 動作列） |
| 這次 | 本課實績：已完成組上→下＝時間序；未做寫 ⏳；剛回報可加粗＋狀態 emoji |
| 上次 DayX | **同課次代號**的上一輪實績（例 Day2→上次 Day2）。沒有寫 — |

```
**動作名**
前三角1.0 二頭0.5

| 目標 | 這次 | 上次 Day2 |
|------|------|-----------|
| … | …✅ | …或 — |
```

一組一排寫在「這次」欄（可用 `｜` 串多組，或表格多列）。略過的 back-off 不要另開「XX BO」列。
✅達標　⚠️偏離　❌未完成　⏳待做　🔧目標已修正。

使用者當場改動作順序 → 整表順序跟著改，剩餘未做動作仍全部列出。

組中不改 e1RM／TM。

## Volume（只接在訓練回覆後面）

由 CLI 或 `core.volume.format_landmarks` 產出。**第一行標題固定 `Volume Landmark區`**，接著兩行 header（ACSM ≥10、Pelland 權重；MEV／MAV／MRV 是 C、不當門）。
然後**一肌群一行**（必須換行，禁止用全形空白併成單行），色點只接在「一週總組」。排序：總組／該肌群跨度，高到低。

要顯示：排課、改表、回報組。不要顯示：諮詢、文獻、閒聊。

權重來源：`config/volume_weights.yaml`（共用預設）；若存在且含 `movements`，`user/volume_weights.yaml` 可本機覆寫。`movements` 沒列到的動作 key **不計入** Volume，不要當場瞎猜權重——缺動作請引使用者看 `CONTRIBUTING.md` 送 GitHub PR 擴充。

改權重檔後，下一則訓練回覆的權重列與計算跟著變。

## 一周怎麼算

不寫死練幾天、不寫死週一。看 `board.yaml` 的 `microcycle_days` 與各日計畫組數。
若離本週 Day 1 已約一週、後面幾練還沒做：問要開下一週（沒跑的留空），還是先跑完再算同一週。

排課／改表的課表表版面 → `plan-reply.md`（權重欄＝fractional；不要把本頁的組紀錄塞進課表）。

## 肌群 allowlist（寫死）

Volume 頁腳與動作權重**只能**用下列繁中名（與 `core.volume.ALLOWED_MUSCLES` 同步）：

`前三角` `中三角` `後三角` `胸` `背闊` `二頭` `三頭` `股四` `股二` `臀` `小腿` `腹`

**禁止**自創或顯示：`斜方`、`上背`、`側三角`、英文肌群名、以及任何未列名。

## 有效組

計入 Volume／進度的工作組須落在該動作當日計畫 RPE／RIR 帶（見 `session-adjust.md`）。不改寫 RPE 帶；**重量日**狀態差先砍組，**量日**先降負荷。
