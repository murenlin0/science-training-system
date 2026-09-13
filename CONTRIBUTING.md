# 貢獻指南（Contributing）

> **PR** 在此指 **GitHub Pull Request**（送 patch 合進倉庫），不是課表裡的 personal record／1RM（那條流程在 `workflows/estimate-pr.md`）。

歡迎 PR，尤其是**新增動作與肌群 fractional 權重**——這讓容量審計能覆蓋更多訓練，而不會把 MEV／MAV／MRV 變成合格門檻。

## 動作權重：`config/volume_weights.yaml`

共用預設改 **`config/volume_weights.yaml`**（不是 `user/`）。格式：

```yaml
movements:
  your_movement_key: [{m: 前三角, w: 1.0}, {m: 三頭, w: 0.5}]
```

- **`your_movement_key`**：與課表／`core/movements.yaml` 的 `key` 一致，建議 **snake_case**。
- **`m`**：肌群**中文短名**，必須是 `config/volume_landmarks.yaml` → `muscles` 底下的 key（例如 `前三角`、`背闊`、`上背`）。拼錯的肌群不會被算進去。
- **`w`**：該動作每 1 工作組，對該肌群算多少「等效組」。

### 預設與原則

| 角色 | 建議 `w` | 說明 |
|------|----------|------|
| 直接刺激（Pelland 式） | ≈ **1.0** | 主動肌群 |
| 協同 | ≈ **0.5** | 常見協同肌 |
| 更細的小數 | 教練粗估 | 請在 PR 說明理由；檔內可加註「教練粗估（C）」 |

- **沒列在 `movements` 的動作**：該組**不計入**容量審計——請**不要**在 PR 裡為未知動作瞎猜權重；若要支援，請一併提供 key 與合理權重。
- **Landmarks（MEV／MAV／MRV）** 仍是 L2 啟發式，僅供審計顯示，**不是** pass／fail 門檻；本倉庫不會為此加 L4 或把 MRV 當擋門。

### 本機覆寫（不必 fork）

若只想自己改、不進共用預設，可放 **`user/volume_weights.yaml`**（已 gitignore），**同一 schema**，且必須含 top-level **`movements`**。程式只在檔案存在且 schema 有效時採用；否則用 `config/`。

Landmarks 同理：`user/volume_landmarks.yaml` 需含 **`header`** 與 **`muscles`** 才會覆寫 `config/volume_landmarks.yaml`。

### PR 描述範本（可貼在 GitHub PR 裡改）

```
新增動作：reverse_fly（反向飛鳥）

- config/volume_weights.yaml：後三角 1.0、上背 0.3（直接／協同對齊 Pelland 預設）
- key 與 session 登錄一致；肌群名來自 volume_landmarks.yaml
- pytest tests/test_volume.py -q 通過
```

### PR 檢查清單（範例）

- [ ] 動作 `key` 為 snake_case，與現有課表／登錄用法一致
- [ ] 每個 `m` 都能在 `config/volume_landmarks.yaml` 找到
- [ ] 直接 ≈1.0、協同 ≈0.5；非整數小數有簡短理由或檔內註解
- [ ] 若有文獻或教練慣例，在 PR 描述註明（可選 `citation_ids` 若已登錄於 `evidence/citations.yaml`）
- [ ] `python -m pytest tests/test_volume.py -q` 通過

## 其他改動

- **L1 原則**（`guardrails/`）：需 A 級文獻依據，請先開 issue 討論。
- **L0 算術**（`core/`）：改動請附測試。

感謝貢獻。
