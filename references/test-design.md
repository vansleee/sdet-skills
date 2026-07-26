# 測試設計原則（reference，被 test-author / test-heal 讀）
避開 flaky 三根源：選擇器穩定（role/testid 優先，避免脆弱 CSS/xpath）、等待正確（web-first assertion，禁 waitForTimeout 蓋時序）、測資獨立（每次乾淨資料、不依賴前一步）。
斷言可讀：失敗訊息要寫給人看，一眼知道「預期什麼、實際什麼」，禁 expect(true).toBe(true) 這類廢斷言。
（待補）
