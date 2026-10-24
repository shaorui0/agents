---
metadata:
  kind: mitigation
  status: draft
  symptom_class: "Cluster 2 — Scheduling/Capacity"
  idempotent: true
  reversibility: R2
  precondition: "StarRocks FE CrashLoopBackOff；fe.log 显示 BDB 元数据记录的是旧 Pod IP；FE 角色停留 UNKNOWN"
  blast_radius: "FE 元数据全部重建，CN 注册与 catalog 需要重跑 init SQL 才能恢复"
  undo: "不存在"
  undo_cost: "不存在"
  invalidating_signal: "若 FE 日志没有 IP 绑定相关报错，删 PVC 不会解决问题，且元数据无法找回"
  derived_from: "cases/case-starrocks-fe-crashloop-bdb-ip-binding.md"
---

# 不可逆动作：删除 FE PVC 重建 BDB

**本条不进止血候选输出。** 删 PVC 等于丢弃 FE 元数据，撤回不存在。

源 case 把它标为「临时修复」，从恢复速度看确实快，但按 T13 门 2 它属于 R2，不能出现在根因未知时的候选列表里。

真正的修复方向是把 FE Service 改成 headless 拿到稳定 DNS，那属于变更管理而非止血。
