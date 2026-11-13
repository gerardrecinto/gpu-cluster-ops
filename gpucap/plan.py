"""Estimate how many GPUs a model needs: weights plus KV cache, with headroom."""
import math
import sys
from dataclasses import dataclass

GIB = 1024 ** 3
BYTES = {"fp32": 4, "fp16": 2, "bf16": 2, "int8": 1, "int4": 0.5}
GPUS_GIB = {"a10g": 24, "l40s": 48, "a100-80": 80, "h100": 80}


@dataclass
class Model:
    params_b: float  # billions
    layers: int
    kv_heads: int
    head_dim: int


MODELS = {
    "llama3-8b": Model(8.0, 32, 8, 128),
    "llama3-70b": Model(70.0, 80, 8, 128),
}


def weights_gib(m, dtype):
    return m.params_b * 1e9 * BYTES[dtype] / GIB


def kv_cache_gib(m, kv_dtype, context, seqs):
    per_token = 2 * m.layers * m.kv_heads * m.head_dim * BYTES[kv_dtype]  # K and V
    return per_token * context * seqs / GIB


def gpus_needed(m, dtype, context, seqs, gpu, utilization=0.9, kv_dtype="fp16"):
    """Smallest GPU count (power of two, for tensor parallelism) whose usable memory fits."""
    need = weights_gib(m, dtype) + kv_cache_gib(m, kv_dtype, context, seqs)  # the KV cache stays fp16 even when weights are quantized
    usable = GPUS_GIB[gpu] * utilization
    n = max(1, math.ceil(need / usable))
    return 1 << (n - 1).bit_length(), round(need, 1)


def main(argv):
    if len(argv) != 6:
        sys.exit("usage: python -m gpucap.plan MODEL DTYPE CONTEXT SEQS GPU")
    _, model, dtype, context, seqs, gpu = argv
    n, need = gpus_needed(MODELS[model], dtype, int(context), int(seqs), gpu)
    print(f"{model} {dtype} ctx={context} seqs={seqs}: {need} GiB -> {n} x {gpu}")


if __name__ == "__main__":
    main(sys.argv)
