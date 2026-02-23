# 4周激进版计划与完成度（面向 Databricks / Cloud Data Engineer JD）

> 基准计划：  
> Week1 重构+测试+基础CI  
> Week2 Azure链路+Secrets  
> Week3 Workflows+Terraform最小集  
> Week4 监控仪表盘+投递材料+模拟面试

更新时间：2026-02-23

## 总体状态
- Week1：进行中（约 75%-85%）
- Week2：未开始
- Week3：未开始
- Week4：部分准备（已有 dashboard 基础），其余未开始

---

## Week1：重构 + 测试 + 基础 CI（进行中）

### 已完成
- [x] 命名与目录统一（direct / landing / platform）
- [x] `databricks.yml` job 路径与新文件名对齐
- [x] Day2 已知问题修复并记录（硬编码表名、`T.col` 风险）
- [x] 抽取可复用 Python 模块到 `src/lakehouse/`
- [x] 补充单元测试到 `tests/unit/`
- [x] 本地测试通过：`7 passed`
- [x] 分支开发流程完成并合并 PR 到 `main`

### 进行中
- [ ] Day3.2 模块接入范围扩大（目前已在部分 notebook 接入，需补齐 direct 全链路）

### 未完成
- [ ] 基础 CI（GitHub Actions：pytest + lint）  
- [ ] Day6 全链路回归（Bronze -> Silver -> Gold -> Observability）证据沉淀  
- [ ] Day7 变更日志与“JD能力映射表”固化

---

## Week2：Azure 链路 + Secrets（未开始）

### 目标
- [ ] Azure 存储/访问链路接入（最小可运行）
- [ ] Secret 管理（Databricks secret scope / key vault 路线）
- [ ] 参数化环境（dev/test/prod 最小区分）

### 交付物建议
- `docs/WEEK2_AZURE_SECRET_SETUP.md`
- `docs/SECURITY_BASELINE.md`
- 一次成功 run 记录（含参数与输出表）

---

## Week3：Workflows + Terraform 最小集（未开始）

### 目标
- [ ] Databricks Workflows 依赖链完善（失败重试/告警策略）
- [ ] Terraform 最小 IaC（workspace 资源最小闭环）
- [ ] bundle 与 IaC 职责边界说明

### 交付物建议
- `infra/terraform/`（最小模块）
- `docs/WEEK3_IAC_WORKFLOWS.md`
- 可复现部署步骤（新环境可跑通）

---

## Week4：监控仪表盘 + 求职材料 + 模拟面试（部分进行）

### 已完成/已有基础
- [x] 已有 Databricks dashboard 初版（可继续强化指标与叙事）

### 待完成
- [ ] 监控仪表盘完善（freshness/completeness/quality/anomaly + SLA阈值）
- [ ] 项目证据包（架构图、运行证据、质量报告、回归报告）
- [ ] 英文/德文项目讲述模板（STAR）
- [ ] 模拟面试题库（Databricks/Azure/Spark/工程化）

---

## 按 JD 的能力映射（当前）

### 已覆盖
- Databricks + Spark + Delta：有实际项目链路与 job 部署
- Python 工程化：模块化 + 单元测试
- 数据建模与分层：Bronze/Silver/Gold + observability
- Git 协作：分支、PR、合并流程

### 待补齐（优先）
- Azure 生产化能力（存储、身份、secret、网络最小认知）
- CI/CD 标准化（actions、lint、test gate）
- IaC（Terraform 最小可复现）
- 生产运行能力证据（告警、回滚、成本优化）

---

## 下周执行优先级（建议）
1. 先补 Week1 未完成项：CI + 全链路回归证据 + JD映射文档。
2. 然后切入 Week2：先做 Secrets，再做 Azure 数据链路。
3. 每完成一项必须有“可展示证据”（命令、截图、run URL、结果表）。

