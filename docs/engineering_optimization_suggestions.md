# Lakehouse 架构与工程化优化建议指南

本文档总结了当前项目中数据管道（Pipeline）与工程化设置（Engineering Setup）的现状梳理，并提供了进阶的优化建议，旨在帮助项目从“探索期脚本”向“企业级成熟架构”平稳演进。

---

## 第一部分：数据管道架构 (Pipeline Architecture)

当前项目实现了典型的 Bronze -> Silver -> Gold 湖仓一体架构，整合了高频交易数据与低频宏观指标（如外汇、利率）。

### 1. 性能优化 (Performance Engine)
* **消除 PySpark UDF 的序列化损耗**：
  * **现状**：在 Silver 层（如处理 FRED/ECB）频繁使用 Python 原生 UDF，导致大量 JVM 与 Python 进程间的跨界序列化开销。
  * **建议**：FRED JSON 应直接使用 Spark SQL 内置的 `from_json()` 及 Schema 原生提取；对于 ECB XML，可使用 Databricks 原生支持的 `from_xml()`，或以 `regexp_extract()` 等原生运算代替 Python 解析逻辑以成百上千倍提升执行速度。
* **避免增量作业的全表扫描与计算**：
  * **现状**：部分 Silver 脚本（如加密货币处理）每次都会读取 Bronze 全表进行 `MERGE INTO`。
  * **建议**：针对 Bronze -> Silver 链路，引入 **Databricks Auto Loader (`cloudFiles`)** 或者基于 **Spark Structured Streaming** 处理增量新文件，避免每小时扫描历史无用基线，提升运行效率并降本。

### 2. 数据模型安全性 (Data Modeling Safety)
* **Forward Fill（向后填充）的越界风险**：
  * **现状**：Gold 层宏观汇总脚本利用不限制范围的 `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` 进行工作日数据到周末的时间对齐。
  * **建议**：宏观填补必须增加“有效存活窗口期（TTL）”打断机制。遇到源数据（由于 API 异常等）停更超过 3~5 天时，业务特征应显式抛出 Null 阻断或触发告警，而非无休止沿用古代过期利率酿成风控事故。

### 3. 可靠的基础设施 (Robust Operations)
* **Bronze 层 API 并发度改造**：
  * **现状**：采用同步睡眠与阻塞式串行拉取接口，回补长达几十天的重载效率极低。
  * **建议**：Python 请求应重构为使用 `asyncio` 异步并发或 `ThreadPoolExecutor` 线程池机制，并配搭基于 Token Bucket（令牌桶算法）的安全限速退避模块防卫外部封禁机制。
* **缺失的物理存储面维护策略**：
  * **现状**：由于高频增量 Append 与 Upsert 注入，底层 Parquet 很容易形成巨量的小文件灾难。
  * **建议**：构建专门的定时 Housekeeping 作业。每周低峰期自动执行 `OPTIMIZE {table_name} ZORDER BY (...)` 治理读时数据倾斜，附带使用 `VACUUM` 回收过期快照节省云上开支。

### 4. 数据可观测性与调度前置 (Observability)
* **被动式滞后质检**：
  * **现状**：目前依赖事后脚本 `96_validation` 对质量和迟滞指标进行纯手工打分评估。
  * **建议**：将防重复、异常极值（open < 0）检测转移至 **Delta Live Tables (DLT)** 的 `EXPECT` 数据约束护栏中。通过自动拦截或告警实现“管道自监控”，并利用 Databricks Workflows 将孤岛 Notebook 串联为编排顺畅的任务依赖网。

---

## 第二部分：项目工程化设置 (Engineering Setup)

项目已建立 `src/`、`tests/`、以及 `.pre-commit-config.yaml`、`pyproject.toml` 等关键目录与规范配置，初具现代软件工程形态，但在云端集群兼容与标准化方面仍需填补短板：

### 1. 规范化 Python 包构建系统 (Build System Integration)
* **现状**：`pyproject.toml` 目前仅作为 Ruff 的配方表，缺乏模块声明机制。在 Notebook 中只能依赖危险的路径注入 `sys.path.insert(0, _local_src)` 强行加载自定义包，在分布式环境中极其易碎。
* **建议**：补充 `[build-system]` 和 `[project]` 元数据定义，使代码成为标准包：
  ```toml
  [build-system]
  requires = ["setuptools>=61.0"]
  build-backend = "setuptools.build_meta"

  [project]
  name = "lakehouse"
  version = "0.1.0"
  description = "Enterprise Databricks Lakehouse Platform"
  requires-python = ">=3.10"
  dependencies = [
      "requests",
      "pyspark>=3.3.0"
  ]
  ```
  完成之后，Job 执行环境可采用 `%pip install -e .` 或 Wheel 包原生化导入 `import lakehouse`。

### 2. 补齐依赖声明与静态类型系统 (Dependencies & Typing)
* **建议**：工程需具备“开箱即用”的一键克隆复现能力。通过 `pyproject.toml` 的 `optional-dependencies.dev` 区块，明确声张诸如 `pytest`, `pre-commit`, `ruff` 等环境版本。对于业务内核包，额外引入 `mypy` 等强制静态类型声明（Type Hints），规避 Python 隐性类型引发的线上解析惨剧。

### 3. Notebook 的全面降级与受控管理 (Thin Notebooks & Fat Modules)
* **现状**：数据流控制（DataFrame Transforms、SQL Aggregations）大量散落在 Jupyter 文件内，避开了局部 CI 检测流程和高速纯 Python 测试。
* **建议**：Notebook 只负责“声明参数”及“调用上层封装方法”这两项超轻量动作（Trigger Runner）。剩余沉重金融计算统统重构为以 DataFrame 作进出参数的独立 Python 函数安放回 `src/lakehouse/`，通过纯洁的 Pytest mock 数据进行闪电验证。

### 4. 消除预提交静态检测盲区 (Notebook Linting)
* **现状**：目前的 `pre-commit` 结合 `Ruff` 仅捕捉清洗了纯 `.py` 脚本文件，任由重要的 Notebook 继续充斥语法告警或未经清理的僵尸引用。
* **建议**：在 `pyproject.toml` 中配置 `tool.ruff.extend-include = ["*.ipynb"]` ，授权工具对 `.ipynb` 内置的 Python 块同样实施无情的缩进格式化清理与代码规约修复。并将手动抽查的数据质量验证封装至 GitHub Actions 等 CI/CD 发版审批流，做到发布前的数据面+代码面双重兜底保驾护航。
