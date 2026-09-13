---
skill: science-training-system
category: planning
description: 先問主項，再查該主項的輔助表，再排課。
---

# 排課

0. **問主項。** 未答完不准排。禁止套預設三大項或肩推／引體／俄挺。
1. 每個主項用 `core/classify.py` 分成 P / B / I。類型 B 要體重。類型 I 沒有 `max_hold_s` → 第一堂只測。
   俄挺當主項：先讀 `literature/assistance/planche.md`（60–70% max-hold，不是 %MVC）。
2. **輔助只查表。** 對已選主項呼叫 `core.assistance.for_primaries(keys)`，讀 `config/assistance.yaml`。看 `support`／`grade`，不要把 ACSM 讀成「這個動作有 RCT」。同一 key 不得再當輔助（`forbid_as_accessory`）。
3. 負荷用 `core/load.py`。類型 B 禁止手算掛重百分比。
4. L1 見 `guardrails/principles.yaml`。L2 數字見 `config/parameters.yaml`。回訓見 `config/retraining.yaml`。
5. 有氧用 `core/karvonen.py`。禁止 220−年齡。
6. 先複述主項 + 輔助候選，等人確認再出完整表。對方說用存檔才讀 `user/athlete.yaml`。
7. **肌群審計（必做，不當門）。** 主項＋輔助定案後，用 `core.volume` 算本週 fractional。回覆附 Volume（先 header：ACSM ≥10、Pelland 權重；再 MEV／MAV／MRV）。有 🔴 先砍輔助／重複刺激，不砍專項主項。目標若不是肥大，不必把「每肌群 ≥10」套到每個協同肌。
8. 一周幾練看這份課表，不要寫死週一或四練。使用者覆寫輔助要記下來，並重跑本步。
