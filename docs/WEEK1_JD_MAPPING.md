# Week1 能力与JD映射（当前真实进度版）

面向岗位：Databricks / Cloud Data Engineer（含 Azure + Databricks 方向）
更新时间：2026-02-25（Week1 冻结版）

## 1) 候选人背景定位
- 学术背景：理论物理博士 + 数学本科/硕士。
- 行业背景：曾在中国民航高校任教。
- 工程化转型证据：已完成 Databricks 项目重构、job 编排、单元测试与 CI 基线。

## 2) JD要求 -> 项目证据 -> 当前状态 -> 缺口 -> 下一步

| JD要求 | 当前项目证据 | 当前状态 | 缺口 | 下一步（4周计划对齐） |
|---|---|---|---|---|
| Databricks / Spark / Delta 实战 | `direct_market_macro_pipeline` + Bronze/Silver/Gold notebooks + bundle deploy/run | 已覆盖（项目级） | 生产运行证据还需更完整 | 补全回归报告与任务级结果截图 |
| Python 可维护与可测试 | `src/lakehouse/*` + `tests/unit/*` + `7 passed` | 已覆盖（基础） | 覆盖率与边界场景不足 | 增加异常/空值/边界测试 |
| CI/CD 基础 | `.github/workflows/ci.yml`（`ruff + pytest`）+ `.pre-commit-config.yaml` | 已覆盖（基础） | 仍缺发布/部署门禁 | Week2/3 增加环境级 gate |
| 命名规范/可维护性 | notebook 命名统一为 `direct_* / landing_* / platform_*` | 已覆盖 | 仍需长期约束机制 | 在 README 加命名规范与检查步骤 |
| Job 编排与依赖管理 | `databricks.yml` 任务链（setup->bronze->silver->gold->obs） | 已覆盖（基础） | 缺失败重试/告警策略说明 | Week3 增强 workflows 策略 |
| Observability | `70_platform_observability_metrics_build.ipynb` + `96_validation_day6_regression_checks.ipynb` + 对应模块抽取 | 基本覆盖 | 仍需一次重跑确认 `FAIL->OK` | Week4 完善 dashboard+阈值 |
| Azure 平台能力（存储/身份/安全） | 目前主要是 Databricks 侧 | 未开始 | Azure 证据不足 | Week2 补 Secrets + Azure 最小链路 |
| Terraform / IaC | 当前未落地 Terraform 代码 | 未开始 | 无 IaC 证据 | Week3 落地最小 Terraform |

## 3) 可直接用于投递/面试的“已完成事实”
- 完成项目结构治理：清理重复链路并统一命名。
- 完成 Databricks bundle 化部署配置（`databricks.yml`）并执行 job run。
- 抽取可复用 Python 模块，避免核心逻辑只留在 notebook。
- 建立单元测试基线，当前 `tests/unit` 通过（7 passed）。
- 落地 GitHub Actions 最小 CI，具备持续验证入口。

## 4) 当前最关键短板（按求职优先级，Week1 结束时）
1. Azure 生产链路证据不足（Secrets、存储、权限、网络）。
2. IaC 缺口（Terraform 未落地）。
3. 监控与运维证据仍不足（SLA、告警闭环、失败处置、成本/SLO 历史趋势）。

## 5) Week2-Week4 面试导向补强路线
1. Week2：补 Azure + Secrets 最小可运行闭环，并记录证据。
2. Week3：补 Terraform 最小资源模板 + 可复现部署说明。
3. Week4：固化监控指标看板 + 形成“项目证据包”（Run URL、截图、SQL结果、变更记录）。

## 6) 面试自述（30秒版）
“我把一个以 notebook 为主、命名混乱的 Databricks 项目重构成了可部署、可测试、可协作的工程化管道：统一了 direct/landing 命名，整理了 job 编排，抽取了可复用 Python 模块并建立了单元测试和 CI。下一步我在 2-3 周内补齐 Azure 与 Terraform 的生产化证据，用完整的回归与监控材料对齐 Cloud Data Engineer 岗位要求。”
