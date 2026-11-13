# GPU serving runbook

## A GPU node throws an XID error (alert: GpuXidError)
1. `kubectl cordon <node>` so nothing new lands on it.
2. `kubectl drain <node> --ignore-daemonsets --delete-emptydir-data`. The PDB keeps one replica up when there are two or more.
3. Check `nvidia-smi -q` and `dmesg | grep -i xid` on the node. Replace the instance if it repeats.
4. The model cache PVC is zonal. A replacement node in another zone cannot mount it, so the pod reloads weights from the Hub. Budget minutes for that.

## Queue backlog (alert: VllmQueueBacklog)
Add replicas if GPUs are free. If not, lower `--max-num-seqs`. Run `python -m gpucap.plan` first to see whether the model and context length fit the GPU you have.

## Disaster recovery
- Everything but the weights is in git: chart, alert rules, Terraform. Rebuild the node group, then `helm install`.
- Weights come from the model hub or your own bucket. Keep a copy in a second region and point `HF_HOME` at it.
- The one thing to decide ahead of time: active/passive (cheaper, minutes to load weights) or active/active (double the GPU bill, no load time).

## Trade-off: Recreate strategy
The chart uses `Recreate`, not a rolling update, because a rolling update needs a second set of GPUs during the rollout. It costs a short outage on every deploy. Switch to rolling when spare GPU capacity is cheap enough or you run 2+ replicas behind a PDB.
