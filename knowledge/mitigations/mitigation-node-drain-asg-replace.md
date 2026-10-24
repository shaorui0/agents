---
metadata:
  kind: mitigation
  status: draft
  symptom_class: "Cluster 2 — Node pressure"
  idempotent: true
  reversibility: R1
  precondition: "已 cordon 且确认问题限于该 node；node 属 ASG 托管；集群有余量承接被驱逐的 pod"
  blast_radius: "该 node 上全部 pod 重新调度，emptyDir 本地数据丢失"
  action: "<kubectl-alias> drain <node> --ignore-daemonsets --delete-emptydir-data，ASG 随后补一台干净新节点"
  undo: "uncordon 原节点并等待 pod 回填；若 ASG 已替换实例则原节点不可恢复，只能靠新节点承接"
  undo_cost: "一次中断"
  invalidating_signal: "node 已 NotReady 时 drain 会挂住；此时应直接走终止实例让 ASG 重建，而不是反复重试 drain"
  derived_from: "cases/case-k8s-pod-evicted-diskpressure-asg-fast-mitigation.md"
---

# 止血候选：drain 并由 ASG 替换节点

需要人给窗口。`--delete-emptydir-data` 会删掉本地临时数据，依赖它的工作负载要先评估。

ASG 替换之后原节点不再存在，所以撤回的语义是「让新节点接住」而非「回到原状态」，这正是它落在 R1 而不是 R0 的原因。
