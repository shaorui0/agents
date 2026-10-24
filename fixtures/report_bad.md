# Triage report: checkout-api p99 latency spike (synthetic, intentionally bad)

## Investigation Plan

phase: A
- H1: something with the database

## Investigation Log

- E1: looked at latency, it was high.
- E2: `db_pool_in_use{service="checkout-api"}` pinned at 50/50.

## Conclusions

- The root cause is the last deploy.
- Pool exhaustion caused the spike [E9].

## Slack Response

The root cause is definitely the connection pool. All customers are affected and this is clearly a database problem.

## Operation Commands

```bash
kprod scale deploy/checkout-api --replicas=1 -n shop
```
