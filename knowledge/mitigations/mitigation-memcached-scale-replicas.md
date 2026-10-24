---
metadata:
  kind: mitigation
  status: draft
  symptom_class: "Cluster 1 — Routing/DNS/Ingress"
  idempotent: true
  reversibility: R0
  precondition: "nginx ingress waiting_latency 周期性尖到约 1.00s 而 upstream_response_time 正常；nginx error log 出现 lua 或 memcached 超时；memcached 为单副本"
  blast_radius: "global_throttle 限流插件的后端缓存，限流判定在扩容瞬间可能短暂不一致"
  action: "把 memcached 扩到 2 个以上副本，并把线程数从 10 提到 32 以上"
  undo: "副本数与线程数改回原值"
  undo_cost: "秒级在线"
  invalidating_signal: "若 waiting_latency 尖峰与 memcached 连接数不相关，或 nginx error log 没有 memcached 超时，说明瓶颈不在这里"
  derived_from: "cases/case-nginx-waiting-latency-memcached-timeout.md"
---

# 止血候选：memcached 扩副本与加线程

无状态缓存，扩缩容都是秒级在线，撤回免费。源 case 里这两条都是 P0。

根因是每请求一次同步 memcached 调用，单副本 10 线程在并发下饱和，连接与读超时阻塞 nginx worker。扩副本消除单点，加线程抬高饱和阈值。
