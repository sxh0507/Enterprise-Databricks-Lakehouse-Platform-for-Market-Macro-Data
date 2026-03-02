# Databricks Lakehouse 工程 `src` 目录架构设计解析

本文档详细解析了项目中 `src/`（Source 目录）的构建思路及其背后的工程化价值。该架构设计旨在将项目从早期的“纯 Notebook 脚本游击队”向“企业级可维护的 Lakehouse 正规军”转型。

## 1. 核心设计理念：Fat Modules & Thin Notebooks（厚模块，薄脚本）

在 Databricks 等云数据平台发展初期，开发者往往会将 API 拉取、JSON 解析、SQL JOIN 等所有逻辑堆砌在长篇大论的 `.ipynb` (Notebook) 文件中。随着业务复杂度上升，这种模式会导致代码难以复用、无法做到本地化单元测试，且维护风险极高。

引入 `src/` 结构的核心思想是：**将“业务逻辑（Logic）”与“执行控制（Runner）”彻底解耦。**

* **业务逻辑（Fat Modules）**：将具体的、可复用的逻辑（如“如何提取特定时间段的 K 线”，“如何进行前向填充关联”）转移到 `src/lakehouse/` 的 `.py` 文件中，成为纯净的 Python 模块。
* **执行控制（Thin Notebooks）**：外层的 Notebook 仅保留轻量级的“控制流”代码，如接收外部参数（Widgets）、加载打包好的 `lakehouse` 模块，并将数据传给底层的函数处理，最终写入 Delta 表。此时的 Notebook 仅扮演“触发器（Trigger）”和“基础设施胶水（Glue）”的角色。

## 2. `src/lakehouse` 内部子模块划分思路

一个设计良好的 `src/` 结构应如流水线般清晰表达数据处理的各个阶段。当前的结构按功能分组（Functional Grouping），划分如下：

### A. 数据摄取层 (`ingestion.py`)
* **职责**：专门负责与外部世界（Coinbase, FRED, ECB 等）进行数据交换。
* **内容**：涵盖 API 请求封装、并发拉取 (`ThreadPoolExecutor`)、异常重试、以及速率限制 (Rate Limiting)。
* **价值**：网络 API 最易发生波动。将其归口隔离后，未来若需调整并发策略或更换数据源，只需触碰该隔离层，不会干扰核心业务逻辑。

### B. 数据解析与标准化 (`parsers/`)
* **职责**：将外部摄入的非结构化/半结构化数据 (JSON, XML) 转换为标准化模型（如 Python Dictionary 或 Spark Rows）。
* **内容**：如 `crypto_parser.py` 解析高频 K 线；`ref_parser.py` 解析由于不同原因合并在一起的低频宏观参考数据（ECB XML 与 FRED JSON）。
* **FRED 解析归属分析**：当前 FRED (JSON) 和 ECB (XML) 解析合并在 `ref_parser.py` 中是合理的。两者同属“慢粒度参考据（Reference Data）”，与极高频的市场交易数据隔离。若未来 FRED 指标爆炸式增长并带有季节性调整等复杂要求时，再进一步拆分为 `fred_parser.py` 和 `ecb_parser.py`。

### C. 特征工程与聚合转换 (`transforms/`)
* **职责**：承载核心的金融计算、多表融合与特征生成。
* **内容**：例如 `macro_builder.py`，接收多张 DataFrame，执行复杂的左连接与带有 TTL 限制的窗口函数前向填充（Forward Fill），吐出特征宽表。
* **价值**：将其搬离长篇 SQL 脚本，封装为 PySpark DataFrame 函数后，最大的成就是**可以在本地利用 Mock 数据进行毫秒级单元测试**，彻底告别必须等待远程云集群启动才能验证代码正误的时代。

### D. 数据质量门禁 (`quality_gate.py` / `xxx_rules.py`)
* **职责**：拦截异常数据落盘，实现主动防御。
* **内容**：统一存放诸如无效 OHLC（开盘价 <= 0）检测、主键重复率校验、宏观特征缺失率计算等规则。
* **价值**：实现了质量规则的“Write Once, Use Everywhere”，既可在 Silver 层清洗时套用防污，亦能在 Gold 层聚合后作为质量监控报警器。

## 3. `src/` 架构带来的三大核心收益

1. **实现零成本的沙盒验证 (Local Unit Testing)**：借助 `tests/` 目录，研发能在本地无 Spark 集群环境下（或伪造单机 Session）高速验证 `macro_builder` 的复杂插补逻辑，大幅缩短研发迭代周期。
2. **强制规范防劣化 (Linter & CI/CD 可观测)**：脱离 Notebook 的散乱束缚后，纯 Python 模块能无缝介入由 Ruff、Mypy 把控的拉取请求保护流 (PR Gate)，强力阻断非标准代码并入主干。
3. **消除重复实现 (Do Not Repeat Yourself)**：解耦后的 Parser 和 Transform 函数能如积木般被任意新分析任务（如新建立一个 1h 粒度的数据管道）随时无缝 `import`，实现工程资产的真正复用。

## 4. 未来的领域驱动进化路径 (Roadmap to DDD)

当代码规模进一步膨胀（超过数十个模块），目前的“扁平化功能分组”可能会略显拥挤，届时架构有必要向**领域驱动设计 (Domain Driven Design)** 演化：

```text
src/lakehouse/
├── core/                 # 底层基建 (Ingestion, Utils)
├── market/               # 【市场交易域】
│   ├── parsers.py        # K线解析
│   ├── rules.py          # OHLC质量校验
│   └── transforms.py     # 波动率与技术因子计算
└── macro/                # 【宏观参考域】
    ├── parsers.py        # 经济/货币政策数据解析 (FRED, ECB)
    ├── rules.py          # 宏观缺失与极值报警
    └── builder.py        # 宏观缝合与对齐机制
``` 

当前的 `src/` 构建已完全符合 Databricks 平台极佳的工程化基准，为下一步业务的弹性扩容奠定了极其扎实的代码基础。
