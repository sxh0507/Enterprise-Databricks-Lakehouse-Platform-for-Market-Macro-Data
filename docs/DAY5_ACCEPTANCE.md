# Day5 Acceptance (Tooling + CI)

## Must pass
- [x] `.github/workflows/ci.yml` 存在
- [x] CI 包含 `ruff` 与 `pytest` 两个检查
- [x] `pyproject.toml` 存在并包含 `ruff` 配置
- [x] `.pre-commit-config.yaml` 存在
- [x] 本地 `ruff` 校验通过（`src` + `tests`）
- [x] 本地 `pytest` 校验通过（`tests/unit`）

## Local validation commands
- `python3 -m ruff check src tests`
- `PYTHONPATH=src python3 -m pytest -q tests/unit`

## Notes
- Day6 重点：补 Databricks 端回归最终状态、任务耗时、表级 SQL 验证输出。
