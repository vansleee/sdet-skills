# Structured Result
把測試/觀察的結果，從「Pass/Fail」二分擴充成六種狀態，每筆附證據。

## 設計理念
- **「Fail」扛太多意思。** 環境掛、時好時壞、證據不足、真 bug 全塞進 Fail，等於沒說。
- **拆開「非 Pass」才報得準。** blocked / inconclusive / anomaly / flaky 各自獨立。
- **錯誤情境被正確擋下 = pass。** 狀態對應「符不符合預期」，不是「畫面上有沒有紅字」。
- **承認不知道是專業。** 誠實的 blocked / inconclusive 比硬給一個不敢信的答案有用。
- **False Positive 的第一道閘。** 只有 fail（及經分類確認的 anomaly）能往下開單。

## 為什麼是六種
**通過只有一種標準：行為符合預期。失敗卻有五種原因** —— 不符合預期（可能是缺陷）、前置沒設起來、結果不穩定、撞到非預期範圍、證據不足。全部塞進 `fail`，等於把五件事講成一件。

六選一不是新發明的分類學，是把那五種各給一格。

## 三組界線與它們的代價
- **blocked ／ inconclusive** —— 沒測到判斷點是 blocked；測到了但看不出來是 inconclusive。實例：snapshot 只讀到「Reltded products」看似整塊不見，但 `GET /products/1` 回 `200`、全頁截圖證實畫面完整 —— 測到了，是工具的觀測時機早於渲染，填 inconclusive。帳號回 `423 Locked` 則是後面全部沒走到，填 blocked。
- **fail ／ anomaly** —— 有明確預期可比對就是 fail；要先有規格才判得動就是 anomaly。實例：購物車數量填 `-5` 顯示負金額，本來就該擋，填 fail；填 `0` 導致單列歸零而總計沒重算，算不算錯要看規格，填 anomaly。**anomaly 讓探索不被帶偏** —— 看到怪東西可以記下來繼續走，不必當場定罪。
- **flaky ／ 穩定壞掉** —— 能穩定重現就是 fail。填了 flaky 就會被當成重試可以蓋掉的東西，這也是本專案 `retries: 0` 的理由。要真的量重現率，交 `flaky-detect`。

## 一個現象可以是兩筆
帳號被鎖：「擋得對」是 pass，「因此測不到的檢查點」是 blocked。混成一筆就會丟掉其中一半的資訊。

## 觀念源頭
James Bach 與 Jon Bach 的 Session-Based Test Management（2000）：一輪測試結束要交 session sheet，交代涵蓋範圍、發現的問題與時間分配。`results.yaml` 是同一件事換成機器讀得懂的形狀 —— session sheet 寫給經理看，`results.yaml` 寫給下一支 skill 吃。

搭配 `evidence-package`；是 `classify-anomaly`、`test-oracle`、`bug-verifier` 的共同詞彙。
