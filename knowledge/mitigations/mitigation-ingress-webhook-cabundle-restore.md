---
metadata:
  kind: mitigation
  status: draft
  symptom_class: "Cluster 6 — Change Management"
  idempotent: true
  reversibility: R0
  precondition: "helm install 报 x509 certificate signed by unknown authority 且点名 webhook；ValidatingWebhookConfiguration 的 caBundle 与 ingress-nginx-admission Secret 的 ca 不一致或为空；近期做过 ingress-nginx 升级"
  blast_radius: "全集群 ingress admission，修复即解锁所有租户的 helm install"
  action: "用 replace 语义把 Secret 里的 ca patch 回 ValidatingWebhookConfiguration 的 caBundle 字段"
  undo: "把 caBundle 改回 patch 前的值（操作前先存一份 -o yaml）"
  undo_cost: "秒级在线"
  invalidating_signal: "若 caBundle 与 Secret 本来就一致，说明失败另有原因，继续 patch 无意义"
  derived_from: "cases/case-ingress-nginx-admission-webhook-cabundle-stale.md"
---

# 止血候选：恢复 admission webhook 的 caBundle

用 `replace` 而不是源 case 里的 `add`。`add` 在字段已存在时会失败，重复执行结果不一致，过不了 T13 门 1 的幂等要求；`replace` 是声明式赋值，重复执行等价。

patch 前先把 ValidatingWebhookConfiguration 存一份 yaml，这就是 undo 的全部内容。
