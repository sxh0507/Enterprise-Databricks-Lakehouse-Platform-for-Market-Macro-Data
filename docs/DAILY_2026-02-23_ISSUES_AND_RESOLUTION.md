# 2026-02-23 问题与处理流程总结

## 今日目标
- 统一项目命名与目录结构，避免 direct / landing 两套路径混乱。
- 完成 Week1 Day3（抽取可测试 Python 模块 + 单元测试）。
- 将最新代码正确同步到 GitHub 与 Databricks，并确保 Job 可运行。

## 今日关键问题与处理记录

### 1) 分支推送失败（non-fast-forward）
- 现象：`git push origin s3-integration` 被拒绝。
- 原因：本地与远端 `s3-integration` 分支分叉（`ahead 4, behind 1`）。
- 处理：
  1. 检查状态：`git fetch origin && git branch -vv && git status`
  2. 同步分支（rebase 或 merge）后再推送。
  3. 推送成功后发起 PR。
- 结果：PR 已成功合并到 `main`。

### 2) Databricks CLI 命令执行报 zsh parse error
- 现象：把带注释的多行命令一次粘贴到 zsh 后报 `parse error near ')'`。
- 原因：shell 对粘贴内容中的注释/特殊字符解析失败。
- 处理：逐行执行纯命令版本：
  - `databricks auth login --host ...`
  - `databricks bundle validate`
  - `databricks bundle deploy`
  - `databricks bundle run direct_market_macro_pipeline`
- 结果：任务进入 `QUEUED -> RUNNING`，部署链路打通。

### 3) Databricks Workspace 仍显示旧文件名
- 现象：仓库已重命名，但 Databricks Git Folder 里仍可见旧命名文件。
- 原因：Databricks Git Folder 缓存/同步状态未刷新，或仍停留在旧 commit/旧分支。
- 处理建议：
  1. 在 Databricks Git Folder 确认分支为 `main`。
  2. 执行 Pull/Update。
  3. 如仍异常，删除该 Git Folder 并从 GitHub 重新 Add Repo。
- 当前结论：GitHub 主仓已是新命名，Databricks 侧可通过重拉/重连解决显示差异。

### 4) src/tests 看起来“空目录”
- 现象：IDE 中目录展开后看起来无文件。
- 原因：通常是 VS Code Explorer 刷新延迟或过滤器影响，不是文件丢失。
- 处理：
  - 用命令确认：`ls -la src/lakehouse tests/unit`
  - 刷新 IDE（Reload Window）或关闭过滤器。
- 结果：模块与测试文件存在且可执行。

### 5) 误提交 `__pycache__` / `.pyc`
- 现象：提交中出现 `__pycache__`、`.pyc` 文件。
- 处理：
  1. 更新 `.gitignore`（`__pycache__/`, `*.py[cod]`, `.pytest_cache/` 等）。
  2. 从索引移除缓存文件并清理目录。
- 结果：缓存产物已从版本控制中清理。

### 6) 命名不一致（旧名与新名混用）
- 现象：notebook、`databricks.yml`、`docs/` 中存在旧名残留。
- 处理：
  - 全量统一命名为 `direct_*` / `landing_*` / `platform_*` 规则。
  - 同步更新 `databricks.yml` 任务路径与文档引用。
- 结果：主流程命名已一致。

## 今日产出（已落地）
- 命名统一后的主流程 notebook 集合（direct/landing/platform）。
- `databricks.yml` 任务链路与新文件名一致，job key：`direct_market_macro_pipeline`。
- Day3 可复用模块：
  - `src/lakehouse/crypto_parser.py`
  - `src/lakehouse/quality_rules.py`
  - `src/lakehouse/observability_rules.py`
- Day3 单元测试：
  - `tests/unit/test_crypto_parser.py`
  - `tests/unit/test_quality_rules.py`
  - `tests/unit/test_observability_rules.py`
- 本地验证：`python3 -m pytest -q tests/unit` 通过（7 passed）。
- GitHub：`s3-integration` PR 已 merged 到 `main`。

## 明日优先动作（建议）
1. 在 Databricks 侧切到 `main` 并重新 Pull；若仍异常，删除旧 Git Folder 后重新 Add Repo。
2. 新建开发分支（例如 `week1-day4-ci`），继续 Day4/Day5：
   - 扩展测试覆盖率；
   - 增加最小 CI（pytest + lint）。
3. 进行一次完整 direct pipeline 回归并保留 run 证据（run URL + 截图 + 输出表）。
