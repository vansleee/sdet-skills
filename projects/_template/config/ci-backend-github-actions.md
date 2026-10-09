# CI 後端：GitHub Actions

「讀 CI run」在 GitHub Actions 上怎麼做（取代舊 Jenkins HTML 解析）。一律用 `gh`。

- 讀失敗 run：`gh run view <run-id> --log-failed`、`gh run view <run-id> --json jobs,conclusion`
- 拿 job / annotation：`gh api repos/{owner}/{repo}/actions/runs/{id}/jobs`
- 下載 Playwright 報告：`gh run download <run-id> -n <artifact-name>`
