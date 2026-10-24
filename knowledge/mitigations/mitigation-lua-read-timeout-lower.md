---
metadata:
  kind: mitigation
  status: draft
  symptom_class: "Cluster 1 — Routing/DNS/Ingress"
  idempotent: true
  reversibility: R0
  precondition: "waiting_latency 的尖峰值恰好等于 Lua read timeout 配置值（例如稳定尖到 1.00s 对应 1000ms 配置）"
  blast_radius: "ingress-nginx 全局限流插件的判定；超时更早触发意味着更多请求走 fail-open 路径"
  action: "ConfigMap 里把 Lua read timeout 从 1000ms 降到 100 到 200ms，ingress-nginx 自动 reload 生效"
  undo: "ConfigMap 改回 1000ms，等待自动 reload"
  undo_cost: "秒级在线"
  invalidating_signal: "若尖峰值与超时配置值不吻合，说明尖峰另有来源，改这个只会掩盖症状"
  derived_from: "cases/case-nginx-waiting-latency-memcached-timeout.md"
---

# 止血候选：调低 Lua read timeout

这一条治的是**症状的上界**而不是根因：把最坏情况的等待从 1s 压到 200ms，为定位争取时间。

尖峰值精确等于超时配置值，本身就是「超时被打满」的强证据，所以前置条件用数值吻合来判定，不靠推测。

判 R0 的理由是 ConfigMap 声明式改值加自动 reload，撤回同样是改值，无连接中断。
