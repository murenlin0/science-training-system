# Changelog

## 0.3.2 — 2026-09-13

- 當日真源改為 `user/session.html`。聊天表只是渲染，不從對話回推。舊 yaml 只在還沒有 html 時讀一次。

## 0.3.1 — 2026-09-13

- 當日每組立刻寫入紀錄並在對話貼表。
- 訓練回覆的容量段先寫每週約 10 組與 fractional 權重，再寫各肌群 MEV／MAV／MRV。
- 類型 B 使用 `one_rm_added` 或 `system_1rm_L`。
