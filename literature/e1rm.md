---
rule_ids: [L0-TYPE-B-SYSTEM-LOAD, L0-TYPE-I]
citation_ids: [zourdos2016, nuzzo2023, lesuer1997, sanchez_moreno2017, scharer2016_hold, wang_shan2023]
---

# 估 PR：按類型，不按動作各寫一條公式

查過可當主項的動作。沒有發表過、且明顯優於現役的肩推／負重引體／俄挺專屬公式。`core/e1rm.py` **維持**。

## 類型 P（槓鈴外載）

有 RPE：JTS／Helms 次數×RPE → %1RM 表，再反推（Zourdos 2016 撐 RIR-RPE）。沒 RPE：Epley `L×(1+reps/30)`。

LeSuer 1997：七條公式相關都很高；Wathan／Mayhew 在蹲／臥上偶爾較準，死拉全體低估。差異在校準，不是「換公式就贏」。Nuzzo 2023 是**力竭次數**↔%1RM，不是 RIR 表，不當替換。人群體重倍數（Strength Level）不當處方。VBT 估 1RM 要裝置；本 skill 不接。

肩推：沒有獨立驗證過、贏過這套的 OHP 公式。低次數（1–5）＋RPE 即可。

## 類型 B（體重＋掛重）

對 **L** 反推再減體重。理由與誤差放大見 `literature/type-b-e1rm.md`。

Sánchez-Moreno 2017：引體 MPV↔%1RM（約 `253.5 − 110.7×MPV`）是 **VBT 監測**，要線性編碼器。不是沒裝置時的現役 e1RM。2020 篇撐 VL／頻率，也不替換 RPE。

## 類型 I（俄挺／前水平）

沒有公斤 1RM。工作組 = `max_hold_s` 的 60–70%。未測只測。

Schärer 2016：吊環 3s→5/7s 加掛重換算，不是地板俄挺秒數定律。Wang & Shan 2023 是肩腕力學，不產 1RM。部落格把力矩換成啞鈴等效，不進層。
