---
metadata:
  kind: mitigation
  status: draft
  symptom_class: "Cluster 2 — Node pressure"
  idempotent: true
  reversibility: R0
  precondition: "故障或压力集中在单个 node（DiskPressure、node 级 DNS 或网络异常、反复 Evicted）"
  blast_radius: "仅该 node 停止接收新 pod，已在其上运行的 pod 不受影响"
  action: "<kubectl-alias> cordon <node>"
  undo: "<kubectl-alias> uncordon <node>"
  undo_cost: "秒级在线"
  invalidating_signal: "若同类症状同时出现在多个 node，说明是集群级或上游问题，隔离单点无效"
  derived_from: "cases/case-k8s-pod-evicted-diskpressure-asg-fast-mitigation.md"
---

# 止血候选：cordon 隔离问题节点

从 drain 里单独拆出来的一步，因为两者撤回成本差一个档。cordon 只改调度开关，uncordon 秒级复原，属 R0；drain 会真的驱逐 pod，属 R1。

先 cordon 能立刻止住「新 pod 继续被调度到坏节点」这条出血点，同时保留全部定位空间。
