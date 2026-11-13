# gpu-cluster-ops

Run LLM inference on GPU Kubernetes nodes: size it, provision the nodes, deploy the server, alert on the GPUs.

- `gpucap/plan.py`: estimates weights plus KV cache and returns the GPU count (power of two, for tensor parallelism).
  `python -m gpucap.plan llama3-70b fp16 8192 8 a100-80` prints `150.4 GiB -> 4 x a100-80`.
- `helm/llm-serve`: vLLM (default) or TGI on GPU nodes. Requests `nvidia.com/gpu`, tolerates the GPU taint, mounts `/dev/shm` for tensor parallel, caches weights on a PVC, has a startup probe and a PDB.
- `terraform/`: EKS GPU managed node group with the NVIDIA AMI, a taint, and scale-to-zero.
- `monitoring/gpu-alerts.yaml`: PrometheusRule for XID errors, temperature, memory, idle GPUs, and vLLM queue depth (DCGM exporter metrics).
- `docs/RUNBOOK.md`: node failure, backlog, and DR, with the trade-offs stated. `docs/CONTROLS.md`: SOC 2 and ISO 27001 mapping.

```bash
python -m pytest -q tests
helm lint helm/llm-serve
```

## Verified
- 5 tests pass. `helm lint` passes and `helm template` renders for both engines (the TGI render sets shard count and GPU limit to 4).
- Alert rules parse as YAML. `terraform fmt` is clean.

## Not verified
- Nothing ran on a GPU or a cluster. The image tags, vLLM and TGI flags, and the health paths come from their docs and were not run.
- Alert rules were not checked with `promtool`, and the metric names were not checked against a live DCGM exporter.
- `terraform validate` did not finish here: the AWS provider plugin timed out on start. Only `terraform fmt` was checked.
- The capacity estimate ignores activation memory and CUDA overhead beyond the 10 percent headroom, so treat it as a lower bound.
