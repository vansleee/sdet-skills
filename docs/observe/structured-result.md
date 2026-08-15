# Structured Result

把測試到的觀察或觀察結果，從 pass 和 fail 的二分法，擴充成六種狀態，而且每一筆都需要附上證據。

## 設計理念

- 因為測試案例失敗，有非常多的原因：有時候可能是環境有問題，有時候可能是這個測試案例的結果時好時壞，那也有時候是證據上可能不足。

  如果我們把真的 bug 和這些測試全部都放在 fail 裡面的話，等於我們沒辦法分清楚哪些是真的 bug，哪些是因為其他原因所導致的 fail。
- 我們必須要把非 pass 的狀態再細切分為 blocked、inconclusive、anomaly 或是 flaky，這樣我們才可以更精確地判斷這些失敗的測試案例。
- 如果今天非預期的情境被測試案例擋下來，這樣的情況我們會視為 PASS。我們會去對應說它符不符合預期，而不是單看 console 上面有沒有錯誤，就判斷它是 FAIL。
- 有的時候，我們必須要承認我們不知道，所以誠實地 blocked 或是 inconclusive，比假想或是推理出一個自己懷疑的答案會更有用。
- 通常 False Positive 是第一道閘門，只有 fail 或是經過我們分類確定的 anomaly，我們才可以繼續往下一步，例如：為這個問題開一張單子。

搭配 `evidence-package`；是 `classify-anomaly`、`test-oracle`、`bug-verifier` 的共同詞彙。
