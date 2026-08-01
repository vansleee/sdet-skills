# Issue Quality Gate

開單前的硬閘門：六條 AND 條件全過才放行，輸出 `output/sessions/<date>_<slug>/gate.yaml` 分流 pass / hold / block。

## 設計理念
- **把好習慣變成硬條件。** 證據（Day 11）、oracle（Day 20）、confidence（Day 22）、非 FP（Day 23）、去重（Day 24）、獨立重現（Day 26）單獨看都是好習慣，但好習慣會被跳過；閘門讓「最好有」變成「沒有就開不了」。
- **AND，不是加權平均。** 五條滿分救不了一條 fail；第一條（可獨立重現）最硬，接的是 Day 14 那句「無法重現就不開單」。
- **被擋下的比放行的更有價值。** 每筆 hold / block 都寫 `blocked_on`，把「agent 判不了、要人來」變成看得到的佇列。
- **透明才能校準。** 擋下的與後來人怎麼判的都進 `output/calibration.yaml`，決定閘門該調鬆或調緊。

## 上下游
上游：`bug-verifier`（verdict）＋ hunter 的 confidence / 指紋 / FP 結果。下游：pass → `triage`（開單）／`bug-fixer`（可修的）；hold / block → 人工佇列。編排它的：`duty-oncall`。

## 成長路徑
v0.1：六條固定檢查。之後：條件可配置化、override 稽核報表。
