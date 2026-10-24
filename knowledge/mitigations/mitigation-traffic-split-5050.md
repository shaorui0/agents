---
metadata:
  kind: mitigation
  status: draft
  symptom_class: "Cluster 7 — Overload/Capacity"
  idempotent: true
  reversibility: R1
  precondition: "尖峰集中在单一集群或单一路径；另一侧集群有承接余量；已确认入口位置与当前路由路径"
  blast_radius: "直接影响客户流量走向，需记录操作人、时间与原因"
  action: "traffic switch 到 gateway 执行 50/50 切分，摊薄单集群峰值压力"
  undo: "把路由权重改回原分布"
  undo_cost: "一次中断"
  invalidating_signal: "若两侧集群共用同一个饱和的下游（同一 DB 或同一 Kafka），切流不减压，只会把问题复制到两边"
  derived_from: "cases/case-large-tenant-qps-spike-joint-mitigation.md"
---

# 止血候选：50/50 切流

权重是声明式的，改回去也是一次改值，但切换瞬间存在连接层面的中断且直接触达客户，所以按 R1 处理，必须由人给窗口并留操作记录。

源 case 的顺序是先降级、再切流、最后带帽扩容。这一条排在 `mitigation-tenant-compute-degradation.md` 之后。
