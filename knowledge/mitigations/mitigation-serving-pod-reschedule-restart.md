---
metadata:
  kind: mitigation
  status: draft
  symptom_class: "Cluster 1 — Routing/DNS/Ingress"
  idempotent: true
  reversibility: R1
  precondition: "连接超时集中在特定 worker node 上的 pod；后端服务本身健康（Service 与 Endpoints 正常）；同 node 直连复现、他 node 不复现"
  blast_radius: "该 deployment 全部 pod 重建并可能落到其他节点，重启期间容量短暂下降"
  action: "重启 serving deployment，让 pod 重新调度到健康节点"
  undo: "无法回到原调度结果；异常时需再次重启或手工约束调度"
  undo_cost: "一次中断"
  invalidating_signal: "若重启后新 pod 仍落在同一坏节点并复现，说明需要先 cordon 该节点再重启，否则只是抽签"
  derived_from: "cases/case-mysql-connect-timeout-fp-dns-node.md"
---

# 止血候选：重启 serving 让 pod 换节点

本质是把「疑似 node 级 DNS 或网络异常」这个未证实的假设，用一次低成本的重新调度来验证兼止血。

正确的组合是先 cordon 坏节点再重启，否则新 pod 有概率被调度回去。这一点写进了 `invalidating_signal`，与 `mitigation-node-cordon.md` 配对使用。
