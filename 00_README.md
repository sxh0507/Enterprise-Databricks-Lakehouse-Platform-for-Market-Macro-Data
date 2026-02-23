# **Enterprise Databricks Lakehouse Platform for Market + Macro Data**
# 
目标：构建可生产化的数据平台（治理/CI/CD/作业编排/可观测）

- **Why this project (Job-aligned)**

对标：Databricks Platform Engineering（UC、RBAC、Jobs、IaC 思维、Data Mesh）

场景：market data + macro reference data（金融企业常见）

- **Architecture (1 张图 + 文字)**

Sources → Bronze → Silver → Gold

Domains：market_data、reference_data

Observability：质量/延迟/缺失率/异常率

- **Tech Stack**

Databricks, Spark/PySpark, Delta Lake, DLT(可选), Unity Catalog

GitHub Actions（CI/CD 示例）

Data quality expectations（或自写 checks）

- **Data Sources**

Crypto：交易所公开 API（OHLC / trades / tickers）

ECB：FX reference rates

FRED：宏观指标（利率/通胀等，日/周频）

- **Data Model**

Bronze：raw JSON + ingestion 元数据

Silver：标准化 schema + 去重 + 统一时区

Gold：marts（K线、波动率/异常、数据健康看板）

- **Pipelines & Jobs**

4 个 jobs：ingest、transform、aggregate、monitor

依赖关系、重试策略、参数化（symbols、日期、环境）

- **Governance (Unity Catalog & RBAC)**

Catalog/Schema 规划

Role → 权限矩阵（platform_admin / data_engineer / analyst）

Goal: Make the platform audit-ready and safe-by-default using a clear namespace, ownership model, and least-privilege access.

Namespace Strategy

We organize assets by domain and medallion layer:

enterprise.bronze_market / enterprise.silver_market / enterprise.gold_market

enterprise.bronze_ref / enterprise.silver_ref / enterprise.gold_ref

enterprise.gold_observability

This naming convention makes lineage and ownership explicit and supports scalable onboarding of new domains.

Roles & Permissions (RBAC)

| Role                     | Bronze       | Silver       | Gold         | Observability |
| ------------------------ | ------------ | ------------ | ------------ | ------------- |
| `platform_admin`         | ALL          | ALL          | ALL          | ALL           |
| `data_engineer`          | READ/WRITE   | READ/WRITE   | READ         | READ/WRITE    |
| `analyst`                | NO ACCESS    | READ         | READ         | READ          |
| `service_principal_jobs` | WRITE (jobs) | WRITE (jobs) | WRITE (jobs) | WRITE         |

Principle: analysts never access raw Bronze; they consume curated Silver/Gold only.

Data Mesh Design (Multi-domain)

This project follows a data mesh-inspired structure with two initial domains:

Domain A: market_data (Crypto)

Sources: exchange public APIs (OHLC/trades)

Outputs: analytics-ready market marts (OHLC, volatility, anomalies)

Domain B: reference_data (ECB / FRED)

Sources: ECB FX reference rates + FRED macro indicators

Outputs: standardized daily reference tables + integrated market-macro mart

Each domain owns its own:

ingestion pipelines (Bronze)

standardization logic (Silver)

data products (Gold)

The gold_observability schema provides cross-domain operational metrics (freshness, quality, completeness) to enforce platform SLAs.











- **Observability**

freshness / volume / completeness / anomaly

输出到 gold_observability.* 表

- **How to Run**
初始化（catalog/schema）

运行 jobs（顺序/参数）

生成 dashboard（可选：SQL Warehouse/DBSQL）

- **CI/CD**

.github/workflows/*：lint + tests + (示例)bundle deploy

dev/staging/prod 配置（可选）

- **Future Work**

DLT 全量化

Terraform 真 IaC

统一数据契约（schema registry / expectations）







# **new_readme**

### Catalog & Namespace Design

This project uses a dedicated Unity Catalog (`enterprise`) to separate
platform-managed data assets from user-level experimentation.

Schemas are organized by both **domain** and **medallion layer**:

- bronze_market / silver_market / gold_market
- bronze_ref / silver_ref / gold_ref
- gold_observability

This structure enables clear ownership, lineage tracking, and
least-privilege access control.


### Data Observability

Operational metrics such as freshness, volume, completeness and anomaly
rates are materialized into a dedicated schema:

`enterprise.gold_observability`

This allows platform operators to monitor pipeline health independently
from business analytics and supports SLA-style governance.




### Data Mesh Design

The platform is organized around independent data domains:

- **market_data**: crypto market OHLC and derived metrics
- **reference_data**: ECB FX rates and FRED macro indicators

Each domain owns its ingestion, transformation logic, and data products,
while sharing common platform services such as observability and governance.



# Enterprise Databricks Lakehouse Platform (Market + Macro Data)

This project implements an **enterprise-style Databricks Lakehouse platform** focused on
**governance, reproducibility, and observability**.  
It ingests crypto market data (Domain A) and is designed to integrate macro reference data
(ECB/FRED, Domain B) to demonstrate a multi-domain, data-mesh inspired architecture.

> Key idea: **data source can change (e.g., Binance → Coinbase)** while the **Silver contract stays stable**.

---

## Why this project (Job-aligned)

This repository is designed to align with **Databricks Platform Engineer / Senior Databricks Engineer** roles:

- **Lakehouse architecture** (Bronze → Silver → Gold, Delta tables)
- **Platform mindset**: auditability, replayability, schema contracts, job orchestration
- **Governance-ready design**: Unity Catalog style namespace, least-privilege access model (RBAC)
- **Observability as first-class citizen**: freshness, volume, quality metrics materialized into tables
- **Data Mesh-inspired domains**: independent domains with shared platform services

---

## Architecture

**End-to-end flow (Domain A: Market Data / Crypto)**

Sources (Coinbase public API)
→ **Bronze** (raw JSON, replayable)
→ **Silver** (standardized schema + dedupe + quality rules)
→ **Gold** (analytics-ready marts + features)
→ **Observability** (pipeline health metrics)

**Domain B (Reference Data / ECB + FRED)** is planned next and will be integrated through Gold marts.

> TODO: Add an architecture diagram image (recommended).  
> Suggested path: `architecture/lakehouse_architecture.png`

---

## Data Mesh design (Domains)

### Domain A: `market_data` (Crypto)
- Ingests OHLC data from exchange public APIs (currently Coinbase)
- Produces standardized Silver tables and Gold marts for analytics

### Domain B: `reference_data` (ECB / FRED) *(next step)*
- ECB FX reference rates
- FRED macro indicators (e.g., FEDFUNDS, CPI)

Each domain owns its ingestion and transformations, while the platform provides:
- governance conventions (namespace + access model)
- cross-domain observability tables

---

## Governance (Unity Catalog / RBAC design)

### Namespace strategy
Assets are organized by **domain** and **medallion layer**:

- `enterprise.bronze_market` / `enterprise.silver_market` / `enterprise.gold_market`
- `enterprise.bronze_ref` / `enterprise.silver_ref` / `enterprise.gold_ref`
- `enterprise.gold_observability`

This structure supports scalable onboarding of new domains and clarifies ownership and lineage.

### Roles & permissions (conceptual RBAC)
| Role | Bronze | Silver | Gold | Observability |
|---|---|---|---|---|
| platform_admin | ALL | ALL | ALL | ALL |
| data_engineer | READ/WRITE | READ/WRITE | READ | READ/WRITE |
| analyst | NO ACCESS | READ | READ | READ |
| jobs_service_principal | WRITE (jobs) | WRITE (jobs) | WRITE (jobs) | WRITE |

Principle: analysts consume curated Silver/Gold only; Bronze remains restricted.

---

## Table overview (Domain A implemented)

### Bronze (raw, replayable)
- `enterprise.bronze_market.crypto_ohlc_raw`  
  Columns: `source, symbol, interval, event_time, raw_json, run_id, ingestion_ts`

### Silver (standardized + deduped)
- `enterprise.silver_market.crypto_ohlc_1m`  
  Columns: `source, symbol, bar_start_ts, bar_end_ts, open, high, low, close, volume, ingestion_ts, p_date`

### Gold (analytics marts)
- `enterprise.gold_market.ohlc_1m`  
  Adds features: returns, rolling MA, rolling volatility, etc.

### Observability (platform metrics)
- `enterprise.gold_observability.pipeline_metrics_daily`  
  Tracks: row count, freshness, null rate, duplicate rate, status

---

## Pipelines (current)

### 1) Bronze ingestion
Notebook: `10_direct_bronze_market_crypto_ingest.ipynb`  
- Parameterized ingestion (symbols, interval, date window)
- `run_id` for audit/replay
- stores **raw JSON as-is**

### 2) Silver transform
Notebook: `20_direct_silver_market_crypto_ohlc_transform.ipynb`  
- Parses raw JSON into standardized schema
- Applies data quality rules
- Dedupes with MERGE (`source + symbol + bar_start_ts`)

### 3) Gold marts
Notebook: `30_direct_gold_market_ohlc_features_build.ipynb`  
- Builds analytics-ready mart with feature engineering (rolling windows)

### 4) Observability
Notebook: `70_platform_observability_metrics_build.ipynb`  
- Materializes freshness/quality/volume metrics into a dedicated table

---

## How to run

### Step 0: Initialize catalog/schema/tables
Run: `00_platform_setup_catalog_schema.ipynb`

### Step 1: Ingest to Bronze
Run: `10_direct_bronze_market_crypto_ingest.ipynb`  
Recommended first run:
- `symbols=BTC-USD` *(or your Coinbase symbol format)*
- `interval=1m`
- `start_date/end_date` empty (default: today UTC)

### Step 2: Transform to Silver
Run: `20_direct_silver_market_crypto_ohlc_transform.ipynb`

### Step 3: Build Gold marts
Run: `30_direct_gold_market_ohlc_features_build.ipynb`

### Step 4: Compute observability metrics
Run: `70_platform_observability_metrics_build.ipynb`

> TODO: Add screenshots as evidence (Jobs DAG, tables in UC, sample queries).

---

## Key design decisions (Interview talking points)

- **Auditability**: raw payloads + run_id + ingestion timestamp in Bronze  
- **Stable contract**: Silver schema remains constant even if data source changes  
- **Idempotence / dedupe**: MERGE into Silver using business keys  
- **Observability**: pipeline health metrics are materialized as tables (not just logs)  
- **Scalability**: domain-based namespace supports onboarding new datasets and teams

---

## Next steps
- Implement Domain B (ECB/FRED): Bronze → Silver → Gold integration
- Add Databricks Jobs workflow (orchestrated DAG) and CI/CD (GitHub Actions + bundles/CLI)
- Add data quality expectations & alerting thresholds








