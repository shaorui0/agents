# Triage report: checkout-api p99 latency spike (synthetic example)

## Investigation Plan

phase: B
- H1: connection pool exhaustion in `checkout-api` after a traffic step
- H2: slow downstream dependency
- Acceptance: root cause hypothesis verified with at least two independent signals; no mutation without approval

## Extracted Signals

- time window: 2026-03-02T10:05Z to 2026-03-02T10:25Z
- cluster: kprod
- namespace: shop
- service: checkout-api
- symptom: p99 latency 2.4s vs baseline 0.3s

## Investigation Log

- E1: `histogram_quantile(0.99, rate(http_request_duration_seconds_bucket{service="checkout-api"}[5m]))` at 2026-03-02T10:12Z: max 2.4s, step jump at 10:07Z, 8.0x baseline.
- E2: `db_pool_in_use{service="checkout-api"}` at 2026-03-02T10:08Z: pinned at 50/50 for 14 min.
- E3: `rate(http_requests_total{service="checkout-api"}[5m])` at 2026-03-02T10:06Z: 1.9x baseline, step at 10:06Z.
- E4: `kprod logs deploy/checkout-api --since=20m | grep "timeout acquiring connection"` at 2026-03-02T10:15Z: 312 matches, first at 10:08Z.

## Conclusions

- Pool exhaustion is consistent with the latency step; the pool was saturated one minute after the traffic step [E2] [E3].
- The latency step starts at 10:07Z, after the traffic step and before the first connection timeout in logs [E1] [E3] [E4].
- No evidence of a downstream dependency slowdown in this window; checked database latency only, other dependencies unknown [E1].

## Slack Response

Evidence suggests the p99 spike on checkout-api is consistent with database connection pool exhaustion following a traffic increase of about 1.9x. Impact scope is unknown; some users may be affected. Next step is a proposed pool size change, awaiting your approval.

## Operation Commands

Draft only. Nothing here has been run; each command awaits explicit approval.

```bash
# INTENT: pool pinned at 50/50 with 312 acquire timeouts, restart to clear stuck connections; expect pool in_use to drop below 50
kprod rollout restart deploy/checkout-api -n shop
```

```bash
# INTENT: preview the pool size change without applying it
kprod apply -f checkout-api-config.yaml -n shop --dry-run=server
```

```bash
kprod rollout status deploy/checkout-api -n shop
```

## Links

- dashboard: https://grafana.example.invalid/d/checkout
- alert: https://alerts.example.invalid/a/123
