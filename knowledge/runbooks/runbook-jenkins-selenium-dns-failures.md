---
metadata:
  kind: runbook
  status: draft
  summary: "Troubleshooting runbook for Jenkins Selenium tests hitting DNS/network errors like net::ERR_NAME_NOT_RESOLVED: covers name resolution and connectivity checks on the Jenkins agent, Kubernetes Service/Ingress validation, common causes, fixes and prevention, plus commands and reasoning from a real case."
  tags: ["jenkins", "selenium", "dns", "networking"]
  first_action: "Run `nslookup` from the agent"
---

# Issue Type: Jenkins — Selenium DNS Failures

## Problem Pattern
- Selenium tests fail with `net::ERR_NAME_NOT_RESOLVED`
- API endpoint connection failures; Jenkins build unstable or failed

## Investigation

### 1. Verify DNS resolution from Jenkins agent
```bash
ssh jenkins-agent
nslookup <target-hostname>
curl -v <api-endpoint-url>
```

### 2. Check K8s resources in the target cluster
```bash
k-prod-a get pods -n qaautotest
k-prod-a get svc -n qaautotest
k-prod-a get ingress -n qaautotest
```

### 3. Common causes

| Cause | Signal |
|-------|--------|
| DNS not resolvable from Jenkins agent | `nslookup` fails on agent but works elsewhere |
| Test environment not deployed | No pods in `qaautotest` namespace |
| Ingress misconfigured | Ingress exists but no matching backend service/endpoint |
| DB connectivity | Services up but app errors on DB queries |

## Resolution Steps

**DNS resolution failure on agent**: update `/etc/hosts` on the Jenkins agent with the correct entry for the target hostname, or fix the DNS configuration so the agent can resolve the domain.

**Services not deployed**: deploy or restart required services in the `qaautotest` namespace on `k-prod-a`.

**DB connectivity**:
```bash
k-prod-a exec -it <mysql-pod> -n database -- mysql -e "SHOW DATABASES LIKE '<app>_prod_ui';"
```

## Reference Case: JENKINS_18988

- **Cluster**: `k-prod-a`
- **Namespace**: `qaautotest`
- **Domain**: `admin-demo2.dv-api.com`

```bash
nslookup admin-demo2.dv-api.com

k-prod-a get pods -n qaautotest
k-prod-a get svc -n qaautotest

k-prod-a exec -it mysql-pod -n database -- mysql -e "SHOW DATABASES LIKE '<app>_prod_ui';"
```

**Root cause**: Jenkins agent could not resolve `admin-demo2.dv-api.com`. Fixed by updating DNS configuration on the agent and ensuring the test environment was deployed in `qaautotest`.
