---
skill: science-training-system
category: session
description: 當日紀錄格式與 Volume 頁腳。真源是 HTML，聊天只是渲染。
---

# 紀錄

真源：`user/session.html`（gitignore）。每次回報組立刻用 `core.session_log.save_session` 寫入。聊天貼的表只是同一份的渲染，不要從對話回推組數或重量。還沒有 html 時，才讀一次舊的 `user/session.yaml`。

## 聊天順序

1. 已完成組（上→下＝時間序）
2. 剛回報的那一組（加粗 + 狀態）
3. 接下來待做（目標改了標 🔧）

每個動作：

```
**動作名**
前三角1.0 二頭0.5

| 目標 | 今日 | 上周 |
|------|------|------|
| … | …✅ | …或 — |
```

一組一排。略過的 back-off 不要另開「XX BO」列。
✅達標　⚠️偏離　❌未完成　⏳待做　🔧目標已修正。

組中不改 e1RM／TM。

## Volume（只接在訓練回覆後面）

呼叫 `core.volume.format_landmarks`。**第一、二行必須是檔裡的 header**（ACSM ≥10、Pelland 權重；MEV／MAV／MRV 是 C、不當門）。
然後全部肌群一行排完，色點只接在「一週總組」。排序：總組／該肌群跨度，高到低。

要顯示：排課、改表、回報組。不要顯示：諮詢、文獻、閒聊。

權重來源：`config/volume_weights.yaml`（共用預設）；若存在且含 `movements`，`user/volume_weights.yaml` 可本機覆寫。`movements` 沒列到的動作 key **不計入** Volume，不要當場瞎猜權重——缺動作請引使用者看 `CONTRIBUTING.md` 送 GitHub PR 擴充。

改權重檔後，下一則訓練回覆的權重列與計算跟著變。

## 一周怎麼算

不寫死練幾天、不寫死週一。看這份課表排了幾練。
若離本週 Day 1 已約一週、後面幾練還沒做：問要開下一週（沒跑的留空），還是先跑完再算同一週。
