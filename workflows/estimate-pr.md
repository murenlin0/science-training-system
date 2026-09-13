---
skill: science-training-system
category: intensity
description: 只要數字、不排整週。先分類再呼叫 e1rm.py。
---

# 估 PR

0. **問動作。** 未說不准猜三大項或肩推／引體／俄挺。
1. `core/classify.py` → P / B / I。讀 `literature/e1rm.md`。公式只走 `core/e1rm.py`，禁止手算類型 B。
2. 收集變數：
   - **P**：重量、次數；有 RPE 用表，沒有才 Epley。
   - **B**：體重必問。掛重、次數、RPE。對 **L** 反推再減體重。沒 RPE 才用 Epley，並警告誤差會被 L÷掛重放大。
   - **I**：沒有公斤 1RM。沒有 `max_hold_s` → 只出測試協議，不估工作組。
3. 回訓見 `config/retraining.yaml`。舊 1RM 不作種。
4. 輸出保守值 + 範圍。2–3 周用 RPE 校。不寫入 `user/` 除非對方點頭。
5. 要排課 → `design-plan.md`。正在練 → `session-adjust.md`。
