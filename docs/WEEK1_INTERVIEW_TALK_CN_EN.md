# Week1 Interview Talk (CN + EN)

## Document Metadata
- Scope: Week1 project summary for interview presentation
- Project: `Enterprise-Databricks-Lakehouse-Platform-for-Market-Macro-Data`
- Week1 period: `2026-02-22` to `2026-02-25`
- Week1 archive completion: `2026-02-26 00:33:37 CET`
- Week1 regression gate: `PASS` (see `docs/WEEK1_REGRESSION_EVIDENCE.md`)

## 1) 中文版（可直接面试讲解）

### 1.1 项目一句话介绍
这是一个基于 Databricks 的市场与宏观数据 Lakehouse 项目，我在 Week1 把“以 notebook 为主、命名不统一、缺少测试和 CI”的版本，重构成了“可部署、可测试、可回归验收”的工程化版本。

### 1.2 项目目标与范围
- 目标：把 direct pipeline 变成可持续迭代的工程项目，而不是一次性 notebook 脚本。
- 范围：Week1 聚焦工程化基础，不涉及完整 Azure/Terraform 生产化落地。
- 产出：命名治理、模块抽取、单测、CI、回归 SQL 验证、JD 映射与面试材料。

### 1.3 技术架构（当前主链路）
- 编排方式：Databricks Asset Bundle（`databricks.yml`）。
- Job：`direct_market_macro_pipeline`。
- 任务链路：
  - `00_platform_setup_catalog_schema.ipynb`
  - `10_direct_bronze_market_crypto_ingest.ipynb`
  - `11_direct_bronze_ref_ecb_fx_ingest.ipynb`
  - `12_direct_bronze_ref_fred_ingest.ipynb`
  - `20_direct_silver_market_crypto_ohlc_transform.ipynb`
  - `22_direct_silver_ref_macro_transform.ipynb`
  - `30_direct_gold_market_ohlc_features_build.ipynb`
  - `32_direct_gold_market_macro_daily_build.ipynb`
  - `70_platform_observability_metrics_build.ipynb`

### 1.4 Week1 执行流程（Day1-Day7）
- Day1-Day2：结构治理与命名统一，清理重复脚本，明确 active pipeline。
- Day3：把 notebook 纯逻辑抽到 `src/lakehouse`（`crypto_parser.py`、`quality_rules.py`、`observability_rules.py`）。
- Day4：补 `tests/unit`，建立本地基线（`7 passed`）。
- Day5：落地 CI（GitHub Actions：`ruff + pytest`），加 pre-commit 规则。
- Day6：新增 `96_validation_day6_regression_checks.ipynb`，跑表存在性、行数、freshness、空值率、缺失日、重复等检查。
- Day7：冻结文档（changelog、JD mapping、STAR），形成可投递证据包。

### 1.5 关键问题与修复（你可以重点讲这一段）
- 问题1：历史命名混乱，任务路径与实际文件不一致。
  修复：统一 direct/landing/platform 命名，并更新 `databricks.yml`。
- 问题2：逻辑全在 notebook，难测试。
  修复：抽模块到 `src/lakehouse` 并补单测。
- 问题3：质量门禁缺失。
  修复：上线 CI（`ruff + pytest`），将本地规则自动化。
- 问题4：observability 出现结构性误报。
  修复：在 `70_platform_observability_metrics_build.ipynb` 修正 freshness 时间列：
  - bronze: `event_time -> ingestion_ts`
  - gold_ref: `trade_date -> mart_ts`

### 1.6 Week1 量化结果（面试可直接引用）
- 回归门禁：`PASS`
- Observability 最新汇总：`OK = 6`
- 主链路目标表存在性：全部 `OK`
- 行数（核心）：`gold_ref.market_macro_daily = 212`，`gold_observability.pipeline_metrics_daily = 78`
- 质量结果（target 口径）：
  - `bad_ohlc_rows = 0`
  - `dup_group_cnt = 0`
  - target `null_rate_eurusd_rate = 0`
  - target `missing_day_ratio = 0 (0/106)`
- 说明：legacy 表仍保留高缺失，仅做历史对照，不作为主链路失败依据。

### 1.7 我在项目中的角色（建议口径）
- 负责从“notebook 交付”转为“工程化交付”的端到端改造。
- 主导命名规范、任务编排、代码模块化、测试基线、CI 门禁、回归验证与文档冻结。
- 输出了可审计证据链：代码变更 + CI + SQL 验证 + 最终 PASS 结论。

### 1.8 对 JD 的匹配点（Databricks/Cloud Data Engineer）
- 已具备：Databricks job 编排、Spark/SQL 数据链路、Python 可测试化、CI 基线、数据质量与可观测校验。
- 当前缺口：Azure 安全与网络、Terraform IaC、生产级告警与成本/SLO。
- 下一步（Week2-Week4）：Azure Secrets/存储最小闭环 -> Terraform 最小模板 -> 监控告警与面试证据包强化。

### 1.9 2 分钟中文口述稿
我这个项目是一个 Databricks 的市场与宏观数据 Lakehouse。Week1 我做的核心不是加新功能，而是把项目从“能跑”升级到“可维护、可验证、可交付”。
具体来说，我先统一了命名和任务编排，修复了 `databricks.yml` 与 notebook 路径不一致的问题；然后把关键逻辑从 notebook 抽到 `src/lakehouse`，并补了单元测试；接着把 CI 建起来，用 `ruff + pytest` 做质量门禁。
在回归阶段，我新增了独立校验 notebook，从表存在性、行数、freshness、空值率、重复、覆盖率等维度做验证。期间最大的技术问题是 observability 的 freshness 列选错，导致结构性误报。我把 bronze 改成 `ingestion_ts`，gold_ref 改成 `mart_ts` 后，最终 observability 汇总变成 `OK=6`，Week1 回归门禁 PASS。
这周的结果是：项目具备了工程化基线，也形成了可面试讲解的证据链。下一步我会在 Week2/3 补齐 Azure 和 Terraform 的生产化能力。

## 2) English Version (Interview-ready)

### 2.1 One-liner
This is a Databricks-based market + macro data lakehouse project. In Week1, I transformed it from a notebook-heavy prototype into an engineering-ready pipeline that is deployable, testable, and regression-validated.

### 2.2 Scope and objective
- Objective: move from “scripts that run” to “pipeline that can be maintained and audited”.
- Scope: Week1 focused on engineering foundations, not full production Azure/Terraform rollout.
- Outputs: naming governance, module extraction, unit tests, CI, SQL-based regression checks, JD mapping, and interview materials.

### 2.3 Current pipeline architecture
- Orchestration: Databricks Asset Bundle via `databricks.yml`.
- Job key: `direct_market_macro_pipeline`.
- Task chain:
  - setup catalog/schema
  - bronze crypto / ecb / fred ingests
  - silver crypto + macro transforms
  - gold feature + macro daily build
  - observability metrics build

### 2.4 Week1 execution flow
- Day1-Day2: structure cleanup, naming standardization, duplicate script archival.
- Day3: extracted reusable logic into `src/lakehouse`.
- Day4: added `tests/unit`, established local baseline (`7 passed`).
- Day5: implemented CI (`ruff + pytest`) and pre-commit checks.
- Day6: added `96_validation_day6_regression_checks.ipynb` and executed SQL validation across Bronze/Silver/Gold/Observability.
- Day7: froze deliverables (changelog, JD mapping, STAR) as interview evidence.

### 2.5 Key issues and fixes
- Issue 1: inconsistent naming and bundle-path mismatch.
  Fix: unified notebook naming and aligned `databricks.yml`.
- Issue 2: critical logic trapped in notebooks.
  Fix: extracted reusable Python modules with unit tests.
- Issue 3: no automated quality gate.
  Fix: enabled CI with lint + tests.
- Issue 4: structural false-fail in observability freshness.
  Fix in `70_platform_observability_metrics_build.ipynb`:
  - bronze freshness column: `event_time -> ingestion_ts`
  - gold_ref freshness column: `trade_date -> mart_ts`

### 2.6 Quantified outcomes
- Week1 regression gate: `PASS`
- Latest observability summary: `OK = 6`
- Target data quality checks passed:
  - `bad_ohlc_rows = 0`
  - `dup_group_cnt = 0`
  - target null rate (`eurusd_rate`) = `0`
  - target missing-day ratio = `0 (0/106)`
- Note: legacy gold table remains as historical reference and is excluded from current target pass criteria.

### 2.7 My role
- Led the end-to-end engineering refactor: naming, orchestration, modularization, tests, CI, regression validation, and documentation freeze.
- Delivered an auditable evidence chain: code + CI + SQL outputs + final PASS gate.

### 2.8 Fit to Cloud Data Engineer JD
- Covered now: Databricks orchestration, Spark/SQL data flow, Python maintainability, unit testing, CI baseline, data quality/observability validation.
- Remaining gaps: Azure platform/security depth, Terraform IaC, production-grade alerting and cost/SLO operations.
- Next (Week2-Week4): Azure minimal secure path -> Terraform minimal IaC -> observability/dashboard hardening.

### 2.9 2-minute English script
In Week1, my goal was to convert a notebook-centric Databricks project into an engineering-ready data pipeline.
I started by standardizing naming and fixing bundle-to-notebook path consistency in `databricks.yml`. Then I extracted core logic from notebooks into reusable Python modules under `src/lakehouse`, and added unit tests to establish a stable baseline.
Next, I implemented CI with `ruff + pytest` and pre-commit checks, so quality validation became automated rather than manual. For regression, I introduced a dedicated SQL validation notebook that checks table existence, row counts, freshness, null rates, duplicate groups, and macro coverage.
The major issue was a false-fail in observability caused by wrong freshness timestamp columns. After correcting those mappings, the latest observability status became `OK=6`, and the Week1 regression gate passed.
This gives me a solid engineering baseline, and in the next phase I will extend this with Azure security and Terraform IaC evidence for production-level readiness.

## 3) Optional Interview Q&A (Quick)

### Q1: Why is your legacy table still failing?
- A: It is intentionally preserved as a historical baseline. Current production target has moved to `enterprise.gold_ref.market_macro_daily`, which passed all target checks.

### Q2: What is your strongest Week1 contribution?
- A: Turning an ad-hoc notebook workflow into an auditable engineering pipeline with repeatable quality gates.

### Q3: What would you do next in 2-3 weeks?
- A: Add Azure secrets + access model, introduce Terraform minimum stack, and implement alerting/SLO-driven observability.
