"""Tracked issues in waybarrios/vllm-mlx.

One record, one file. See AGENTS.md for the schema and the rules.
"""

REPO = 'waybarrios/vllm-mlx'

# number -> severity / headline / why it matters.
ISSUES = {546: {'severity': 'high',
       'headline': 'Strict json_schema decode wedges with no token progress',
       'why': 'Over 5-minute hangs on Qwen3-Coder-30B-A3B. Structured output is load-bearing '
              'for tool arguments.'},
 570: {'severity': 'medium',
       'headline': 'Qwen3.6-35B-A3B dequantize shape mismatch (works in mlx-vlm)',
       'why': 'Same class as mlx-lm #1197: mlx-vlm handles a checkpoint the mlx-lm path does '
              'not.'},
 584: {'severity': 'high',
       'headline': 'Non-loopback requests silently dropped on --host 0.0.0.0',
       'why': 'Deployment blocker: a server on the LAN is reachable only from localhost. '
              'Silent — no log, recv-queue 0.'},
 590: {'severity': 'medium',
       'headline': 'Gemma 4 TextModel dispatch, logit_bias API, and MLLM fallback stalls',
       'why': 'Dispatch falls through to qwen3_5 rather than the Gemma path.'},
 619: {'severity': 'high',
       'headline': 'Hardcoded mx.set_cache_limit(32GB) is not device-scaled',
       'why': 'Filed as an OOM on small Macs, but it cuts the other way here: a hardcoded 32GB '
              'ceiling on a 256GB box leaves most of the machine unused.'},
 627: {'severity': 'medium',
       'headline': 'memory_budget_gb never reconciled with the Metal allocation ceiling',
       'why': 'Two allocators with different ideas of the budget. Relevant when hot-swapping '
              'checkpoints for A/B runs.'},
 641: {'severity': 'high',
       'headline': 'MemoryAwarePrefixCache stores caches by reference',
       'why': 'Leaks Metal buffer handles on hybrid models. Compounds every other '
              'memory-pressure item at concurrency.'},
 658: {'severity': 'low',
       'headline': 'Validate Qwen MoE MTP conversion artifacts before decode',
       'why': 'Would catch a broken MTP head at load instead of at generation.'},
 668: {'severity': 'critical',
       'headline': 'DeepSeek V4 Flash unsupported',
       'why': 'ValueError: Model type deepseek_v4 not supported. Open since 2026-08-01, no '
              'maintainer reply, no PR — and mlx-lm has no deepseek_v4.py, so the architecture '
              'is unimplemented upstream too.'},
 672: {'severity': 'high',
       'headline': 'Streaming tool calls can end without finish_reason',
       'why': 'A tool call that ends without a terminator is exactly the shape that reads as a '
              'fabricated turn downstream.'},
 678: {'severity': 'high',
       'headline': 'Prefix cache trims RotatingKVCache past its window',
       'why': 'Cross-conversation KV leak and repetition loops. A correctness bug, not a speed '
              "bug — one tenant's context bleeding into another's is disqualifying for "
              'multi-agent serving.'},
 682: {'severity': 'medium',
       'headline': 'Closing a stream leaves the inner generator and request state open',
       'why': 'Client disconnects are routine in agentic work; leaked request state '
              'accumulates.'},
 689: {'severity': 'medium',
       'headline': 'Completion cache can store desynchronized rotating KV state',
       'why': 'Another way the cache serves state that does not match the prompt it is keyed '
              'on.'},
 699: {'severity': 'high',
       'headline': 'DFlash and DSpark draft heads block speculative decoding',
       'why': 'Both are the vendor-shipped draft mechanisms on the models that have one. If '
              'neither is wired up, speculative decoding on this engine is limited to what the '
              'generic k=1 path gives you.'},
 710: {'severity': 'high',
       'headline': 'MTP drafting pinned to k=1 on hybrid linear-attention',
       'why': 'Reference CUDA/vLLM deployments run k=3 at ~77% acceptance for a ~66% decode '
              'gain. Measured on Qwen3.8-27B / M3 Ultra 256GB: verify forward is 69% of step '
              'time, reject and replay 19.3%.'},
 711: {'severity': 'medium',
       'headline': '--prefill-step-size silently dropped under --continuous-batching',
       'why': 'Prefill chunk size is the main Apple Silicon prefill lever, ignored in exactly '
              'the config we would run.'},
 725: {'severity': 'medium',
       'headline': 'PR: GLM-4.7 thinking streams into content, not reasoning_content',
       'why': 'With --reasoning-parser glm4 the entire thinking block lands in content. '
              'Non-streaming is unaffected, so it is easy to miss - an agent frontend renders '
              "the model's reasoning as the visible reply."},
 729: {'severity': 'medium',
       'headline': 'PR: honor --prefill-step-size with continuous batching',
       'why': 'One of two competing fixes for #711.'},
 730: {'severity': 'critical',
       'headline': 'Prefix-cache reuse silently disabled for hybrid architectures',
       'why': "#691's all-or-nothing rewind gate rejects every hybrid model: ArraysCache "
              'leaves have no .keys and inherit is_trimmable() -> False. Measured on '
              'Qwen3.8-27B-8bit — an identical 24k prompt resent back-to-back gives zero '
              'speedup on main, versus ~58x before #691. Rejection logs only at DEBUG.'},
 731: {'severity': 'critical',
       'headline': 'PR: make prefix-cache rewind gate aware of non-KV hybrid leaves',
       'why': 'Explicitly Fixes #730, opened 2026-08-25 with the 58x measurement attached. The '
              'single event that most changes this plan.'},
 732: {'severity': 'medium',
       'headline': 'PR: surface prefix-cache reuse via '
                   'usage.prompt_tokens_details.cached_tokens',
       'why': 'Observability. Without it there is no way to confirm a hit rate from the API — '
              'which is how #730 stayed silent.'}}
