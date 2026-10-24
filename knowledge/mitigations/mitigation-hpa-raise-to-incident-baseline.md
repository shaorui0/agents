---
metadata:
  kind: mitigation
  status: draft
  symptom_class: "Cluster 7 — Overload/Capacity"
  idempotent: true
  reversibility: R0
  precondition: "serving 或 async pod 已顶到当前 HPA 上限；且 DB 饱和度指标仍有余量（这一条必须先核对）"
  blast_radius: "对应 deployment 的副本数与其下游连接数"
  action: "把 serving / async 的 HPA max 提到事故基线档位，保留显式上限，禁止解除封顶"
  undo: "HPA max 改回事故前档位"
  undo_cost: "秒级在线"
  invalidating_signal: "DB 饱和度已达上限时本条失效且有害，扩容会把 DB 推过临界点；此时应先降级或切流"
  derived_from: "cases/case-large-tenant-qps-spike-joint-mitigation.md"
---

# 止血候选：HPA 上限提到事故基线

撤回是改回一个数字，秒级在线，所以判为 R0。但它是 R0 档里**唯一一条前置条件必须硬核对**的：源 case 的安全边界写明「先降级再扩容，DB 没余量时扩 serving 或 async 会加重事故」。

保留封顶而不是解除封顶，是为了让这次动作本身仍然处在一个已知的容量包络内。
