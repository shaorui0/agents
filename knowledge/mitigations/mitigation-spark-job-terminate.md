---
metadata:
  kind: mitigation
  status: draft
  symptom_class: "Cluster 2 — Scheduling/Capacity"
  idempotent: true
  reversibility: R1
  precondition: "job_id 已定位；pod 长期停在 Pending、Init 或 Terminating，从未进入 Running；worker pool 被占住导致后续作业排队"
  blast_radius: "该作业本次运行作废，占用的 worker 槽位释放"
  action: "通过 DCluster 终止卡住的作业，必要时回收 worker pool"
  undo: "重新提交该作业"
  undo_cost: "一次中断"
  invalidating_signal: "若 spark-master 本身未 ready，终止单个作业不解决问题，新提交的作业会同样卡住"
  derived_from: "cases/case-spark-job-pending-not-running.md"
---

# 止血候选：终止卡死的 Spark 作业

撤回的形式是重跑，代价是一次作业运行时间，不涉及数据丢失，所以落在 R1 而不是 R2。

前置条件里「从未进入 Running」很关键：已经跑到一半的作业终止后重跑，代价与风险都不同，不适用本条。
