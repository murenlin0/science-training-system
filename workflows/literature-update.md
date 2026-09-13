---
skill: science-training-system
category: maintenance
description: 文獻進層規則。AI 在對話裡判斷，不寫爬蟲、不自動合併。
---

# 文獻更新

使用者丟論文或說「查一下 X」時：

1. 讀原文或可靠摘要。不要靠記憶編造 DOI。
2. 先判層，再改檔：
   - 算錯／定義錯 → L0 `core/identities.yaml` + 測試。不需要論文。
   - Position Stand 或高質量統合分析要改原則 → 討論後才動 L1。單篇 RCT 不改 L1。
   - 數字、輔助菜單、啟發式 → L2。
   - 工具／模板 → L3。完整西岸包裝、功能性訓練品牌、ACWR 傷害規則 → `evidence/rejected.yaml`。
3. 新來源登記 `evidence/citations.yaml`（id、ref、grade）。規則只寫 `citation_ids`。
4. 輔助若因文獻增刪：改 `config/assistance.yaml` + 對應 `literature/assistance/*.md` 的 `rule_id`。
5. 改完跑 `python -m pytest tests -q`，再 `graphify update .`。
