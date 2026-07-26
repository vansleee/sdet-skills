# Structured Result
把測試/觀察的結果，從「Pass/Fail」二分擴充成六種狀態，每筆附證據。

## 設計理念
- **「Fail」扛太多意思。** 環境掛、時好時壞、證據不足、真 bug 全塞進 Fail，等於沒說。
- **拆開「非 Pass」才報得準。** blocked / inconclusive / anomaly / flaky 各自獨立。
- **錯誤情境被正確擋下 = pass。** 狀態對應「符不符合預期」，不是「畫面上有沒有紅字」。
- **承認不知道是專業。** 誠實的 blocked / inconclusive 比硬給一個不敢信的答案有用。
- **False Positive 的第一道閘。** 只有 fail（及經分類確認的 anomaly）能往下開單。

搭配 `evidence-package`；是 `classify-anomaly`、`test-oracle`、`bug-verifier` 的共同詞彙。
