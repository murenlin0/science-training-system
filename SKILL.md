---
name: science-training-system
description: 科學力量訓練——先問主項，再按四層規則排課。選完主項只讀該 key 的輔助對照表。類型 B 百分比打在總系統負荷。無預設動作組。
version: 0.3.2
---

# Science-training-system

先問主項，再按四層規則排課。公式在 `core/`。

真資料在 `user/`（gitignore）。只有對方說用存檔才讀。Skill 裡的模板是空的。

## 路由

| 觸發 | 讀什麼 |
|------|--------|
| 只要估 PR／1RM | `workflows/estimate-pr.md` |
| 已有表要改 | `workflows/modify-plan.md` |
| 排完整計畫 | `workflows/design-plan.md` |
| 問為什麼／怎麼／應該 | `workflows/consult.md` |
| 只要體能／GPP | `workflows/conditioning-plan.md` |
| 開練／回報組／下一組／紀錄格式 | `workflows/session-adjust.md` + `workflows/logging.md` |
| 文獻要不要進層 | `workflows/literature-update.md` |
| 算重量／掛重／等長秒 | `core/load.py`（禁止手算類型 B） |
| 選完主項要輔助 | `config/assistance.yaml` → `core/assistance.py` |
| 肌群容量審計 | `core/volume.py`（只接訓練回覆，不當門） |
| 想加動作／肌群權重進共用預設 | `CONTRIBUTING.md` → 改 `config/volume_weights.yaml` 送 **GitHub PR**（不是估 1RM 的 PR） |

## 強制（L0 + L1）

0. 先問主項。禁止預設三大項，也禁止預設肩推／引體／俄挺。
1. 對齊目標再套 `guardrails/principles.yaml`。
2. 類型 B：L = 體重 + 掛重。百分比只打在 L。
3. 主項不力竭。同一動作不能既是主項又是輔助。
4. GPP 不反向改主項。有氧用 %HRR。不用 ACWR。回訓不用舊 1RM。

L2（含輔助菜單、硬拉組數、48h）是參考，不擋課表。

## 輔助

選完主項後呼叫 `core.assistance.for_primaries([...])`。沒有「掃一整本資料庫再猜」。清單是菜單；專項性才是原則。每筆看 `support`：principle／class／exercise／biomech／coach。有引用不是該動作有 RCT。
