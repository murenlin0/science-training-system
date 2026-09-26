# Changelog

## Unreleased

- `board.yaml` 支援 list schema（`days[].exercises`、`active_day: dayN`）與既有 dict schema 並存。
- `python -m core.session_cli`：`open-day`／`skip-day`／`log-set`／`volume`，從 `user/board.yaml` 管線化當日紀錄與 Volume 頁腳。
- Volume 頁腳改為 `Volume Landmark區` 標題＋一肌群一行；`ALLOWED_MUSCLES` 過濾非法肌群權重。
- Skill 路由：開練／跳過／回報組先呼叫 CLI，再在 `session-adjust.md` 做 Δ 自調。

## 0.3.2 — 2026-09-13

- 當日真源改為 `user/session.html`。聊天表只是渲染，不從對話回推。舊 yaml 只在還沒有 html 時讀一次。

## 0.3.1 — 2026-09-13

- 當日每組立刻寫入紀錄並在對話貼表。
- 訓練回覆的容量段先寫每週約 10 組與 fractional 權重，再寫各肌群 MEV／MAV／MRV。
- 類型 B 使用 `one_rm_added` 或 `system_1rm_L`。
