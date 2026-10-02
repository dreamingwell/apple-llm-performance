#!/usr/bin/env python3
"""The decode ceiling: how fast a model *cannot* go on a given Mac.

This is arithmetic over published specifications, in the same class as the
memory-fit figures the page already computes. It is not a measurement and it is
not a prediction of what you will see. It is an upper bound.

    tokens/second <= bandwidth / (bytes the engine must read per token)

Autoregressive decode at batch 1 reads, for every single token it emits, the
whole of the active weight set plus whatever it attends over in the KV cache.
Almost nothing is reused between steps, so the arithmetic units spend their time
waiting on memory. That makes peak memory bandwidth a hard ceiling on decode,
and on Apple silicon the bandwidth figure is a published specification of the
chip - which is why this can be computed rather than guessed.

Bytes per token:

    active weights = build_gb * (active parameters / total parameters)
    KV read        = bytes_per_token * context
    ceiling        = chip bandwidth / (active weights + KV read)

Everything the formula needs is already on this page: `PARAMS_B` and
`ACTIVE_PARAMS_B` in the model record, the measured `gb` of the chosen rung in
its ladder, `KV["bytes_per_token"]` derived from its `config.json`, and `bw`
from data/machines.py.

**Where this is wrong, and by how much.**

- *It is a ceiling, not an estimate.* Real decode lands below it. The published
  measurements collected in `SPEEDS` are the evidence for how far below, and the
  page renders that comparison rather than asserting an efficiency constant.
  Sparse MoE at batch 1 does especially badly against the bound: each expert's
  weight read is small and scattered, so the memory system never gets near peak.
- *It assumes uniform bits per weight.* `build_gb * active/total` is only the
  active byte count if the whole checkpoint is quantised the same way. Two
  models here break that. ds4's builds quantise routed experts to 2 bits while
  leaving dense, shared and attention tensors at Q8/F32, so the active slice is
  denser than the average and the real byte count is higher - the ceiling is
  too high. Qwen3.8-Flash-Next carries a 51B n-gram embedding table that is
  looked up sparsely rather than streamed, so its average is dragged the other
  way.
- *It assumes the whole KV cache is read.* Sparse-attention models (DeepSeek's
  DSA, MiniMax Sparse Attention, Qwen Sparse Attention) select a subset of the
  cache per token, so their KV term is an overestimate at long context and the
  ceiling falls faster with context than reality does.
- *Expert-pruned builds are excluded entirely.* Pruning removes experts the
  router was not going to pick anyway, so it buys memory, not speed: a 350 GB
  and a 451 GB REAP build of the same model decode at the same rate. Scaling by
  `build_gb` would claim otherwise, so pruned rungs get no ceiling at all.
- *It says nothing about prefill.* Prefill is a batched matmul over the whole
  prompt - compute-bound, not bandwidth-bound - so this formula does not apply
  to it. Published prefill figures are recorded and shown; they are never
  estimated.
- *It ignores speculative decoding.* An MTP or draft head emits several tokens
  per weight read, so a measurement can legitimately exceed the bound. That is
  why a `SPEEDS` record may declare `speculative`, and why validate.py only
  rejects an over-ceiling measurement that does not.
- *Multi-machine pooling does not raise it.* Pipeline parallelism splits the
  layers, so each token still traverses all of them in sequence: the bytes and
  the time are the same, plus a Thunderbolt hop per token. The ceiling is
  computed from one machine's bandwidth however many machines are pooled, and
  is optimistic there because the hop is not modelled.

The browser recomputes the same three lines live for the selected cluster; the
JavaScript in tracker/render_status.py carries a pointer back to this file. Keep
the two identical.
"""

# Reasons a ceiling cannot be computed, in the words the page uses.
NO_ACTIVE = "no published active-parameter count"
NO_KV = "no per-token KV cost derived"
PRUNED = "expert-pruned build: per-token traffic does not scale with file size"
NATIVE = "not an autoregressive decoder"


def active_gb(build_gb, active_b, params_b):
    """Gigabytes of weight the engine reads to emit one token."""
    if not build_gb or not active_b or not params_b:
        return None
    return build_gb * (active_b / params_b)


def kv_gb(bytes_per_token, context):
    """Gigabytes of KV cache read per token at the given context length."""
    if not bytes_per_token or not context:
        return 0.0
    return (bytes_per_token * context) / 1e9


def per_token_gb(build_gb, active_b, params_b, bytes_per_token, context):
    w = active_gb(build_gb, active_b, params_b)
    if w is None:
        return None
    return w + kv_gb(bytes_per_token, context)


def ceiling_tps(bw_gbs, build_gb, active_b, params_b, bytes_per_token, context):
    """Upper bound on decode tokens/second. None when the inputs are missing."""
    per = per_token_gb(build_gb, active_b, params_b, bytes_per_token, context)
    if not per or not bw_gbs:
        return None
    return bw_gbs / per


def rung_reason(rung):
    """Why a ladder rung gets no ceiling, or None if it can have one."""
    kind = rung.get("kind")
    if kind == "pruned":
        return PRUNED
    if kind == "native":
        return NATIVE
    return None
