---
metadata:
  kind: mitigation
  status: draft
  symptom_class: "Cluster 7 — Overload/Capacity"
  idempotent: true
  reversibility: R0
  precondition: "单租户 QPS 尖峰已确认；serving 侧 error rate 或 P95/P99 上升；非关键的 hotspot recompute / agg backfill 仍在跑"
  blast_radius: "仅该 tenant 的 Recompute 与 AggBackfill，实时 serving 链路不受影响"
  action: "TenantInfo 里设 hotspotRecomputeTaskRateLimitPerPartition = 0 且 hotspotAggBackfillTaskRateLimitPerPartition = 0"
  undo: "把两个 rateLimit 改回事故前原值"
  undo_cost: "秒级在线"
  invalidating_signal: "若压力来自 DB 饱和或 ingress 连接排队而非计算任务，降级后 P99 不回落，说明本条无效，应转向切流或 ingress 扩容"
  derived_from: "cases/case-large-tenant-qps-spike-joint-mitigation.md"
---

# 止血候选：关闭租户级非关键计算

声明式设值，无需重启，是这个 symptom class 里撤回最便宜的一档，所以排在切流与扩容之前。

把限流设为 0 会暂停 Recompute 与 AggBackfill，代价是数据新鲜度下降与 lag 累积，**不构成数据丢失**。稳定之后按原值逐步恢复。

顺序纪律来自源 case：先降级再扩容。DB 没有余量时扩 serving 或 async 会把 DB 推过临界点。
