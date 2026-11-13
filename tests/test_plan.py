from gpucap.plan import MODELS, gpus_needed, kv_cache_gib, weights_gib


def test_weights():
    assert round(weights_gib(MODELS["llama3-8b"], "fp16"), 1) == 14.9


def test_kv_cache_per_token_is_128_kib_for_8b():
    # 2 * 32 layers * 8 kv heads * 128 dim * 2 bytes = 131072 bytes
    assert kv_cache_gib(MODELS["llama3-8b"], "fp16", 1, 1) * 1024 ** 3 == 131072


def test_8b_fits_one_a100():
    assert gpus_needed(MODELS["llama3-8b"], "fp16", 8192, 8, "a100-80")[0] == 1


def test_70b_fp16_needs_tensor_parallel_and_rounds_to_power_of_two():
    n, _ = gpus_needed(MODELS["llama3-70b"], "fp16", 8192, 8, "a100-80")
    assert n == 4  # about 150 GiB needed, 72 GiB usable per GPU -> 3, rounded to 4


def test_smaller_gpu_needs_more():
    small = gpus_needed(MODELS["llama3-8b"], "fp16", 8192, 8, "a10g")[0]
    assert small > gpus_needed(MODELS["llama3-8b"], "fp16", 8192, 8, "h100")[0]


def test_quantized_weights_do_not_shrink_the_kv_cache():
    m = MODELS["llama3-70b"]
    _, int4 = gpus_needed(m, "int4", 8192, 8, "h100")
    assert int4 == round(weights_gib(m, "int4") + kv_cache_gib(m, "fp16", 8192, 8), 1)
