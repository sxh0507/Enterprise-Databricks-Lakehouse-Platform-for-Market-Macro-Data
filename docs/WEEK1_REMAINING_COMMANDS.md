# Week1 剩余项命令清单（可复制执行）

适用仓库路径：
`/Users/shixiaohong/Downloads/github_projects/Enterprise-Databricks-Lakehouse-Platform-for-Market-Macro-Data`

---

## 0) 进入项目 + 开新分支

```bash
cd "/Users/shixiaohong/Downloads/github_projects/Enterprise-Databricks-Lakehouse-Platform-for-Market-Macro-Data"
git checkout main
git pull origin main
git checkout -b week1-ci-regression-jd
```

---

## 1) 落地最小 CI（pytest）

### 1.1 创建 workflow 文件

```bash
mkdir -p .github/workflows
cat > .github/workflows/ci.yml <<'YAML'
name: ci

on:
  push:
    branches: [ main, week1-ci-regression-jd ]
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
YAML
```

### 1.2 本地先验

```bash
PYTHONPATH=src python3 -m pytest -q tests/unit
```

---

## 2) 执行 direct pipeline 回归并留证据

### 2.1 Databricks 登录与部署

```bash
databricks auth login --host https://dbc-ccc612b1-3dfb.cloud.databricks.com
databricks bundle validate
databricks bundle deploy
```

### 2.2 运行 Job

```bash
databricks bundle run direct_market_macro_pipeline
```

### 2.3 查询运行历史（可选）

```bash
databricks jobs list | head
```

---

## 3) 生成 Week1 回归证据文档

### 3.1 从模板生成文件

```bash
cp docs/WEEK1_REMAINING_TEMPLATES.md /tmp/_wk1_templates_backup.md
cat > docs/WEEK1_REGRESSION_EVIDENCE.md <<'MD'
# Week1 回归证据

## A. 执行信息
- 日期：
- 执行人：
- 分支：week1-ci-regression-jd
- Databricks Workspace：https://dbc-ccc612b1-3dfb.cloud.databricks.com
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
MD
```

---

## 4) 生成 JD 映射文档

```bash
cat > docs/WEEK1_JD_MAPPING.md <<'MD'
# Week1 能力与JD映射（Databricks / Cloud Data Engineer）

## 候选人背景摘要
- 理论物理博士 + 数学背景
- 完成 Databricks Lakehouse 项目重构与作业部署
- 已具备 Python 模块化 + 单元测试基础

## JD要求 -> 项目证据 -> 缺口 -> 下一步
| JD要求 | 当前项目证据 | 当前状态 | 缺口 | 下一步 |
|---|---|---|---|---|
| Databricks / Spark / Delta | Bronze/Silver/Gold + databricks.yml job | 已覆盖 | 性能优化 | 增加性能基线 |
| Python 工程能力 | src/lakehouse + tests/unit | 已覆盖 | 覆盖率可提升 | 增加边界测试 |
| CI/CD | .github/workflows/ci.yml | 已起步 | lint/质量门禁缺失 | 加 ruff |
| Azure | 尚未落地 | 未开始 | 云上链路证据缺失 | Week2执行 |
| Terraform/IaC | 尚未落地 | 未开始 | IaC证据缺失 | Week3执行 |
| 监控治理 | observability notebook | 部分覆盖 | SLA告警缺失 | Week4完善 |
MD
```

---

## 5) 提交并推送

```bash
git add .github/workflows/ci.yml \
        docs/WEEK1_REMAINING_TEMPLATES.md \
        docs/WEEK1_REMAINING_COMMANDS.md \
        docs/WEEK1_REGRESSION_EVIDENCE.md \
        docs/WEEK1_JD_MAPPING.md

git commit -m "docs/week1: add CI+regression+JD templates and execution commands"
git push origin week1-ci-regression-jd
```

---

## 6) 发起 PR（到 main）

```bash
echo "Open GitHub and create PR: week1-ci-regression-jd -> main"
```

PR 标题建议：
- `docs(week1): add CI workflow, regression evidence, and JD mapping`

PR 描述建议：
- Added minimal GitHub Actions CI for unit tests
- Added Week1 regression evidence template and JD mapping document
- Added copy-paste command checklist for execution
