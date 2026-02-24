# Week1 剩余项模板（CI + 回归证据 + JD映射）

更新时间：2026-02-23

---

## 1) CI 模板（最小可用）

### 1.1 目标
- 在 GitHub 上对每次 Push / PR 自动执行：
  - Python 语法检查（可选）
  - 单元测试：`tests/unit`

### 1.2 工作流模板（保存到 `.github/workflows/ci.yml`）

```yaml
name: ci

on:
  push:
    branches: [ main, s3-integration ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install test deps
        run: |
          python -m pip install --upgrade pip
          python -m pip install pytest

      - name: Run unit tests
        env:
          PYTHONPATH: src
        run: |
          python -m pytest -q tests/unit
```

### 1.3 CI 验收记录模板

```md
## CI 验收记录
- 日期：
- 分支：
- 触发方式：push / pull_request
- GitHub Actions run 链接：
- 结果：PASS / FAIL
- 失败原因（如有）：
- 修复 commit：
```

---

## 2) 回归证据模板（Bronze -> Silver -> Gold -> Observability）

> 建议把本节填完后保存为：`docs/WEEK1_REGRESSION_EVIDENCE.md`

```md
# Week1 回归证据

## A. 执行信息
- 日期：
- 执行人：
- 分支：
- Databricks Workspace：
- Job Key：direct_market_macro_pipeline
- Run URL：
- 运行结果：SUCCESS / FAILED

## B. 任务级状态
| task_key | status | duration | 备注 |
|---|---|---|---|
| platform_setup_catalog_schema |  |  |  |
| direct_bronze_market_crypto_ingest |  |  |  |
| direct_bronze_ref_ecb_fx_ingest |  |  |  |
| direct_bronze_ref_fred_ingest |  |  |  |
| direct_silver_market_crypto_ohlc_transform |  |  |  |
| direct_silver_ref_macro_transform |  |  |  |
| direct_gold_market_ohlc_features_build |  |  |  |
| direct_gold_market_macro_daily_build |  |  |  |
| platform_observability_metrics_build |  |  |  |

## C. 数据验收（抽样）
| 层级 | 表名 | 校验SQL | 结果 |
|---|---|---|---|
| Bronze | enterprise.bronze_market.crypto_ohlc_raw | SELECT COUNT(*) ... |  |
| Silver | enterprise.silver_market.crypto_ohlc | SELECT COUNT(*) ... |  |
| Gold | enterprise.gold_market.market_macro_daily | SELECT COUNT(*) ... |  |
| Obs | enterprise.gold_observability.pipeline_health | SELECT COUNT(*) ... |  |

## D. 质量与可观测性
- freshness 指标：
- completeness 指标：
- duplicate_rate 指标：
- 异常样本：

## E. 问题与修复
| 问题 | 影响 | 修复动作 | 关联提交 |
|---|---|---|---|
|  |  |  |  |
```

---

## 3) JD 映射模板（投递版）

> 建议把本节填完后保存为：`docs/WEEK1_JD_MAPPING.md`

```md
# Week1 能力与JD映射（Databricks / Cloud Data Engineer）

## 候选人背景摘要（2-3行）
- 理论物理博士 + 数学背景
- 已完成 Databricks Lakehouse 实战项目（direct + landing 双链路）
- 具备 Python 模块化、测试与作业编排经验（项目级）

## JD要求 -> 项目证据 -> 缺口 -> 下一步
| JD要求 | 当前项目证据 | 当前状态 | 缺口 | 下一步 |
|---|---|---|---|---|
| Databricks / Spark / Delta | Bronze/Silver/Gold 全链路 notebook + job | 已覆盖 | 生产级优化 | 增加性能基线 |
| Python 工程能力 | `src/lakehouse` + `tests/unit` | 已覆盖 | 覆盖率还不高 | 扩展测试场景 |
| CI/CD | GitHub Actions（待落地） | 进行中 | 缺 workflow | 完成 `ci.yml` |
| Cloud/Azure | 暂未落地 | 未开始 | Azure链路 | Week2完成最小闭环 |
| IaC/Terraform | 暂未落地 | 未开始 | IaC证据缺失 | Week3最小Terraform |
| 监控与治理 | observability notebook + UC 命名规范 | 部分覆盖 | SLA/告警薄弱 | Week4补监控告警 |

## 面试可讲故事（STAR）
### 故事1：命名混乱与双路径治理
- S（场景）：direct/landing 两条链路命名混乱，维护成本高。
- T（任务）：统一命名、减少重复、保证 job 可运行。
- A（行动）：重命名 notebook、更新 `databricks.yml`、清理归档、校验路径。
- R（结果）：作业链路可部署运行，文档与代码命名一致。

### 故事2：从 Notebook 到可测试模块
- S：核心逻辑全在 notebook，难测难复用。
- T：抽出可复用模块并建立单测基线。
- A：新增 `src/lakehouse` 与 `tests/unit`，覆盖 parser/quality/observability。
- R：`pytest` 通过（7 passed），后续重构风险降低。

## 一句话电梯陈述（面试开场）
“我把一个偏 notebook 形态的 Databricks 项目重构成了可部署、可测试、可追踪的工程化管道：统一了 direct/landing 命名，落地了 bundle job，抽出了 Python 模块并补齐单元测试，下一步是补 Azure 与 Terraform 的生产化证据。”
```

