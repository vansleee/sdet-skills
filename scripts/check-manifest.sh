#!/usr/bin/env bash
# 檢查登錄、重複名稱與必要入口；只依賴既有文風檢查所需的 Python 3。
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 - <<'PYTHON'
import json
import re
import sys
from collections import Counter
from pathlib import Path

manifest = json.loads(Path('.claude-plugin/plugin.json').read_text())
declared = manifest['skills']
actual = {'./' + str(p.parent) for p in Path('skills').rglob('SKILL.md')}
problems = []
for path, count in Counter(declared).items():
    if count > 1:
        problems.append(f'重複登錄：{path}')
for path in sorted(set(declared) - actual):
    problems.append(f'找不到 SKILL.md：{path}')
for path in sorted(actual - set(declared)):
    problems.append(f'尚未登錄：{path}')
names = []
for path in sorted(actual):
    skill = Path(path) / 'SKILL.md'
    content = skill.read_text()
    frontmatter = re.match(r'\A---\s*\n(.*?)\n---(?:\n|$)', content, re.S)
    name = re.search(r'^name:\s*([a-z0-9-]+)\s*$', frontmatter[1], re.M) if frontmatter else None
    if not name or name[1] != skill.parent.name:
        problems.append(f'name 必須符合目錄名稱：{skill}')
    else:
        names.append(name[1])
    agent = skill.parent / 'agents/openai.yaml'
    if not agent.is_file():
        problems.append(f'缺少 agents/openai.yaml：{path}')
        continue
    explicit = bool(frontmatter and re.search(r'^disable-model-invocation:\s*true\s*$', frontmatter[1], re.M))
    policy = re.search(r'^  allow_implicit_invocation:\s*(true|false)\s*$', agent.read_text(), re.M)
    if explicit and (not policy or policy[1] != 'false'):
        problems.append(f'user-invoked skill 必須停用隱含呼叫：{agent}')
    elif not explicit and policy:
        problems.append(f'model-invoked skill 應省略 invocation policy：{agent}')
for name, count in Counter(names).items():
    if count > 1:
        problems.append(f'重複 skill 名稱：{name}')
if problems:
    print('\n'.join(problems), file=sys.stderr)
    sys.exit(1)
print(f'manifest 與 skill 入口一致：{len(declared)} 支 skill')
PYTHON
