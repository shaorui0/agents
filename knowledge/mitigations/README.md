---
metadata:
  kind: reference
  status: draft
  summary: "止血候选库索引：按撤回成本分档的可逆缓解动作，供 quick check 的 sub-agent 6 检索"
  tags: ["index", "mitigation", "quick-check", "stop-the-bleeding"]
  first_action: "按 symptom_class 定位，再按 reversibility 档位取舍"
---

# Mitigations（止血候选库）

止血发生在**根因未知**的时刻，动作正确的概率天然低于定位之后。所以这个库的准入门槛不是「有没有用」，是**「错了能不能便宜地退回来」**。

判据取自 `rules/axioms/t13_sre_as_nested_control_loop.md` §1，两道门依次过：

| 门 | 内容 | 未过 |
|---|---|---|
| 门 1 · 必要条件 | 能否表达为幂等函数 `f(state) = f(f(state))` | 不进库 |
| 门 2 · 充分条件 | 撤回这个动作要付多少代价 | 分 R0 / R1 / R2 |

| 档 | 撤回成本 | 在 quick check 里 |
|---|---|---|
| **R0** | 秒级在线 | 首选候选，直接列命令 |
| **R1** | 一次中断 | 列出，强制标「需人给窗口」 |
| **R2** | 不存在 | **不列命令**，只输出一行不可逆说明 |

R2 条目仍然收录，作用是让 quick check 在命中这类方向时能正确输出「不可逆，需 full triage 后人工决策」，而不是把它漏掉或误列为候选。

校验：`python3 tools/agent_ops/lint_mitigations.py`（exit 0 = PASS）

## 索引

### R0 · 撤回秒级在线（6 条）

| 文件 | symptom_class | 前置条件 |
|---|---|---|
| [mitigation-hpa-raise-to-incident-baseline.md](./mitigation-hpa-raise-to-incident-baseline.md) | Cluster 7 — Overload/Capacity | serving 或 async pod 已顶到当前 HPA 上限；且 DB 饱和度指标仍有余量（这一条必须先核对） |
| [mitigation-ingress-webhook-cabundle-restore.md](./mitigation-ingress-webhook-cabundle-restore.md) | Cluster 6 — Change Management | helm install 报 x509 certificate signed by unknown authority 且点名 webh… |
| [mitigation-lua-read-timeout-lower.md](./mitigation-lua-read-timeout-lower.md) | Cluster 1 — Routing/DNS/Ingress | waiting_latency 的尖峰值恰好等于 Lua read timeout 配置值（例如稳定尖到 1.00s 对应 1000ms… |
| [mitigation-memcached-scale-replicas.md](./mitigation-memcached-scale-replicas.md) | Cluster 1 — Routing/DNS/Ingress | nginx ingress waiting_latency 周期性尖到约 1.00s 而 upstream_response_time … |
| [mitigation-node-cordon.md](./mitigation-node-cordon.md) | Cluster 2 — Node pressure | 故障或压力集中在单个 node（DiskPressure、node 级 DNS 或网络异常、反复 Evicted） |
| [mitigation-tenant-compute-degradation.md](./mitigation-tenant-compute-degradation.md) | Cluster 7 — Overload/Capacity | 单租户 QPS 尖峰已确认；serving 侧 error rate 或 P95/P99 上升；非关键的 hotspot recompu… |

### R1 · 撤回是一次中断（5 条）

| 文件 | symptom_class | 前置条件 |
|---|---|---|
| [mitigation-async-consumer-restart.md](./mitigation-async-consumer-restart.md) | Cluster 3 — Stateful/Write Pressure | 同一 consumer group 多 topic 同时 lag 上升；下游 ClickHouse 出现 Delaying insert… |
| [mitigation-node-drain-asg-replace.md](./mitigation-node-drain-asg-replace.md) | Cluster 2 — Node pressure | 已 cordon 且确认问题限于该 node；node 属 ASG 托管；集群有余量承接被驱逐的 pod |
| [mitigation-serving-pod-reschedule-restart.md](./mitigation-serving-pod-reschedule-restart.md) | Cluster 1 — Routing/DNS/Ingress | 连接超时集中在特定 worker node 上的 pod；后端服务本身健康（Service 与 Endpoints 正常）；同 node… |
| [mitigation-spark-job-terminate.md](./mitigation-spark-job-terminate.md) | Cluster 2 — Scheduling/Capacity | job_id 已定位；pod 长期停在 Pending、Init 或 Terminating，从未进入 Running；worker p… |
| [mitigation-traffic-split-5050.md](./mitigation-traffic-split-5050.md) | Cluster 7 — Overload/Capacity | 尖峰集中在单一集群或单一路径；另一侧集群有承接余量；已确认入口位置与当前路由路径 |

### R2 · 撤回不存在（3 条）

| 文件 | symptom_class | 前置条件 |
|---|---|---|
| [mitigation-ch-zombie-system-log-drop.md](./mitigation-ch-zombie-system-log-drop.md) | Cluster 3 — Stateful/Write Pressure | ClickHouse 报 Code 241 MEMORY_LIMIT_EXCEEDED；system.tables 里存在 _N 后缀的… |
| [mitigation-kafka-partition-increase.md](./mitigation-kafka-partition-increase.md) | Cluster 3 — Stateful/Write Pressure | MirrorMaker 或 consumer 吞吐顶到每分区上限；租户 QPS 已抬升；topic 分区数明显偏少 |
| [mitigation-starrocks-fe-pvc-recreate.md](./mitigation-starrocks-fe-pvc-recreate.md) | Cluster 2 — Scheduling/Capacity | StarRocks FE CrashLoopBackOff；fe.log 显示 BDB 元数据记录的是旧 Pod IP；FE 角色停留 … |

## 新增条目

调查结束沉淀新止血动作时，先过两道门再写文件，frontmatter 必填字段见 `lint_mitigations.py` 的 `REQUIRED`，`symptom_class` 必须取自其中的 `CLUSTERS` 规范集。

`invalidating_signal` 是硬性要求：止血在根因未知时执行，必须同时给出「什么信号出现说明这条用错了」，否则它是一个没有终止条件的赌注。

新条目 `status: draft` 起步，人工 review 后升 `stable`，与 `/sre-oncall-compound-learning` 的复利治理规则一致。

