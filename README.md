# agents

一个 SRE on-call 分诊 agent，做成 Claude Code skill。告警进去，结构化调查出来。

## 这里有什么

```
SKILL.md              入口：Layer 0 信号提取 → 路由到具体 type skill
ARCHITECTURE.md       分层结构与状态流转
facets/               外部接口的抽象面（告警接入、信号提取、状态库、流量接口）
skills/               可复用的子能力
  sre-oncall-init             建工作目录、提取信号、路由
  sre-oncall-quick-check      快相：先止血还是先定位
  sre-oncall-query-safety     查询安全规则（label filter / step floor / time ceiling）
  sre-oncall-output-format    输出契约
  sre-oncall-acceptance-criteria  什么算调查完成
  sre-oncall-compound-learning    调查结束后的知识写回
  workflow-oncall-spike       延迟毛刺的两阶段 triage
knowledge/            方法论层
  patterns/           反复出现的失败形态
  debug-trees/        分层诊断树
  checklists/         固定核对项
  mitigations/        止血动作，按可逆性分级
  cards/              速查卡
  references/         术语、分类法、查询模板
```

## 设计立场

**自主权绑定在动作的可逆性上。** 幂等可表达是必要条件，撤回成本是充分条件。据此把动作分成三档：秒级在线可撤回、撤回需要一次中断、撤回不存在。只有第一档允许 agent 直接给出命令，第三档永不给。

**actuator 的输出是命题，不是状态变更。** 这条让调查路径可以放开：agent 输出的是「我认为是什么、建议怎么做」，执行留给人。生产侧保持只读。

**上下文按层次固定，不按时间滑动。** 原始指标与日志检索推进子 agent，主循环只收结构化摘要，判断留在主循环里。

**知识随每次调查复利。** 每次调查结束后把增量写回 knowledge/，下一次调查先检索再动手。

## 不在这里的东西

真实事故写作（cases/、runbooks/）、运行时工具与审计日志（tools/）、调查记录（records/）都没有发布。它们含具体的生产环境信息与客户标识。这个仓库只发结构与方法。

## Progress

| Change | Date | What | Takeaway | Links |
|---|---|---|---|---|
| c0001-requirements-and-method | 2026-10-24 | Model (METHOD), requirements and data boundary, change-loop skill, leak-scan tool | Label every safety claim enforced or advised; only an exit code is safety | [report](reports/0001-requirements-and-method.html) · [note](notes/blog/0001-requirements-and-method.md) |
| c0002-deterministic-gates | 2026-10-24 | Gate 3 (`k8s_gate`) with fail-closed tiers and hard blocks, audit pre/post pair, settings example, 37 tests | The gate is the one layer the model cannot negotiate with; fail-closed is a default, not a feature | [report](reports/0002-deterministic-gates.html) · [note](notes/blog/0002-deterministic-gates.md) |
