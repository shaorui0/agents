---
metadata:
  kind: mitigation
  status: draft
  symptom_class: "Cluster 3 — Stateful/Write Pressure"
  idempotent: true
  reversibility: R1
  precondition: "同一 consumer group 多 topic 同时 lag 上升；下游 ClickHouse 出现 Delaying inserting block 或 parts 暴涨；consumer 进程处于卡死或退避重试循环"
  blast_radius: "该 consumer group 一次 rebalance，重启期间 lag 短暂继续上涨"
  action: "重启 async-consumer pods"
  undo: "重启本身不可撤回；异常时回到重启前状态需再等一次 rebalance 收敛"
  undo_cost: "一次中断"
  invalidating_signal: "若下游 ClickHouse 的 insert 延迟与 parts 数依然高企，重启只会让 lag 再次堆积，瓶颈在 sink 而非 consumer"
  derived_from: "cases/case-kafka-lag-issues.md"
---

# 止血候选：重启 async consumer

重启是幂等的（重复执行终态一致），但代价是一次 rebalance 中断，所以是 R1 而非 R0。

这一条容易被误用：源 case 的结论是「lag 加上 Delaying inserting block 要先按下游写入瓶颈处理」。consumer 重启只在 consumer 自身卡死时有效，因此 `invalidating_signal` 直接指向下游指标。
