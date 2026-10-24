---
metadata:
  kind: mitigation
  status: draft
  symptom_class: "Cluster 3 — Stateful/Write Pressure"
  idempotent: true
  reversibility: R2
  precondition: "ClickHouse 报 Code 241 MEMORY_LIMIT_EXCEEDED；system.tables 里存在 _N 后缀的巨型系统日志表；近期做过 CH 升级"
  blast_radius: "删除的系统日志表数据永久消失，历史 trace 与 profile 查询能力一并失去"
  undo: "不存在"
  undo_cost: "不存在"
  invalidating_signal: "若内存尖峰与这些表的 merge 时间不吻合，说明 OOM 另有来源，删表既无效又不可逆"
  derived_from: "cases/case-clickhouse-system-log-zombie-tables-oom.md"
---

# 不可逆动作：DROP `_N` 僵尸系统日志表

**本条不进止血候选输出，只作为不可逆说明存在。** quick check 命中这个 symptom class 时输出一行「该方向的根治动作不可逆，需 full triage 后人工决策」，不给命令。

理由是 T13 门 2：数据删除的撤回不存在，因此决策必须前移到人，agent 只做审计。真正执行走 full triage 的 Phase C 加四关 Mutation Approval Gate。

同一 case 里的 `TRUNCATE` 无后缀活跃表同样是数据删除，同判 R2。
