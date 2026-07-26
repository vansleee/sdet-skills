# Ask SDET
所有 user-invoked skill 的路由器。

## 設計理念
- **治理 cognitive load。** user-invoked skill 不佔 context、但要人記得它存在；一多就記不住。router 是這個負荷的直接解藥。
- **只路由 user-invoked。** model-invoked skill 會自己觸發，不列進來避免雜訊。
- **同時是流程圖。** 除了「用哪個」，還告訴你「它前後接什麼」。
- **必須跟著長。** 新增/改名/移位任何 user 入口都要更新——過時的 router 會誤導。
