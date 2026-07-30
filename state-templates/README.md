# 狀態檔範本

跨 skill 資料流檔的空白範本。用法：複製到 **repo 根目錄**、去掉 `.example`，就成了真檔。

```bash
cp state-templates/issues-index.example.yaml issues-index.yaml
```

真檔含實際判斷結果，已 gitignore，不進版控。

每個檔誰寫、誰讀、存什麼，見 `docs/state-files.md`。那份是唯一權威，本目錄只放範本。
（`config/` 與 `knowledge/` 的範本不在這裡，它們跟各自的真檔同資料夾。）
