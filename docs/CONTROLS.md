# SOC 2 and ISO 27001 mapping

A mapping of what the repo produces as evidence. It is not an audit result.

| Need | Where |
|---|---|
| Change management (SOC 2 CC8.1, ISO A.8.32) | Chart, rules, and Terraform live in git and change through review |
| Secrets (ISO A.8.24) | The chart reads `HF_TOKEN` from an existing Secret and stores none |
| Least privilege (SOC 2 CC6.1) | GPU nodes are tainted. Only pods that request a GPU run there |
| Monitoring (SOC 2 CC7.2) | `monitoring/gpu-alerts.yaml` |
| Availability (SOC 2 A1.2) | PDB, startup probe, runbook |
