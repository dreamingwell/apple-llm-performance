#!/usr/bin/env python3
"""Render the vllm-mlx watchlist state file into a model-first status page."""
import os, re, html, datetime, hashlib, json
from engines import (ENGINES, ENGINE_BY_ID, EMETA, MATRIX, BEST, engine_order,
                     repo_label, CROSS_BY_ENGINE, RELEASE_FEEDS, FAM, FAM_OVERRIDE,
                     BANDS, FIDELITY_NOTES, USE_CASES)
from quants import LADDERS, KV, PARAMS


def card_name():
    """Content-hashed social card filename; CDN caches images for 4h."""
    p = os.path.join(ASSETS, "og-card.jpg")
    if not os.path.exists(p):
        return "card.jpg"
    h = hashlib.sha256(open(p, "rb").read()).hexdigest()[:10]
    return f"card-{h}.jpg"

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(ROOT, "assets")
SITE = os.path.join(ROOT, "docs")
STATE = os.path.join(HERE, "watch-state.txt")

# key -> (severity, headline, why it matters)
META = {
    "waybarrios/vllm-mlx#730": ("critical", "Prefix-cache reuse silently disabled for hybrid architectures",
        "#691's all-or-nothing rewind gate rejects every hybrid model: ArraysCache leaves have no .keys and inherit is_trimmable() -> False. Measured on Qwen3.8-27B-8bit — an identical 24k prompt resent back-to-back gives zero speedup on main, versus ~58x before #691. Rejection logs only at DEBUG."),
    "waybarrios/vllm-mlx#731": ("critical", "PR: make prefix-cache rewind gate aware of non-KV hybrid leaves",
        "Explicitly Fixes #730, opened 2026-08-25 with the 58x measurement attached. The single event that most changes this plan."),
    "waybarrios/vllm-mlx#710": ("high", "MTP drafting pinned to k=1 on hybrid linear-attention",
        "Reference CUDA/vLLM deployments run k=3 at ~77% acceptance for a ~66% decode gain. Measured on Qwen3.8-27B / M3 Ultra 256GB: verify forward is 69% of step time, reject and replay 19.3%."),
    "ml-explore/mlx-lm#1446": ("medium", "ArraysCache is not trimmable",
        "The structural reason the k=1 cap exists — GDN state layers cannot be rolled back on draft rejection. Same root cause as #730."),
    "waybarrios/vllm-mlx#711": ("medium", "--prefill-step-size silently dropped under --continuous-batching",
        "Prefill chunk size is the main Apple Silicon prefill lever, ignored in exactly the config we would run."),
    "waybarrios/vllm-mlx#729": ("medium", "PR: honor --prefill-step-size with continuous batching",
        "One of two competing fixes for #711."),
    "waybarrios/vllm-mlx#678": ("high", "Prefix cache trims RotatingKVCache past its window",
        "Cross-conversation KV leak and repetition loops. A correctness bug, not a speed bug — one tenant's context bleeding into another's is disqualifying for multi-agent serving."),
    "waybarrios/vllm-mlx#641": ("high", "MemoryAwarePrefixCache stores caches by reference",
        "Leaks Metal buffer handles on hybrid models. Compounds every other memory-pressure item at concurrency."),
    "waybarrios/vllm-mlx#689": ("medium", "Completion cache can store desynchronized rotating KV state",
        "Another way the cache serves state that does not match the prompt it is keyed on."),
    "waybarrios/vllm-mlx#658": ("low", "Validate Qwen MoE MTP conversion artifacts before decode",
        "Would catch a broken MTP head at load instead of at generation."),

    "waybarrios/vllm-mlx#668": ("critical", "DeepSeek V4 Flash unsupported",
        "ValueError: Model type deepseek_v4 not supported. Open since 2026-08-01, no maintainer reply, no PR — and mlx-lm has no deepseek_v4.py, so the architecture is unimplemented upstream too."),
    "ml-explore/mlx-lm#1332": ("high", "DeepSeek-V4 unbounded Metal residency during decode",
        "Dies at ~11k decode tokens with metal::malloc resource-limit exceeded. Even once the architecture lands, this has to be fixed before the model is servable."),
    "ml-explore/mlx-lm#1443": ("high", "DSA Indexer sparse top-k evicts attention sinks",
        "Past index_topk (2048) the indexer drops the attention sinks and decode collapses into repetition — a sharp cliff, not drift. Hits every sparse-attention model: DeepSeek V3.2/V4 and GLM-5.2 both decode through this module."),

    "ml-explore/mlx-lm#1418": ("critical", "GLM-5.2 fails to load — missing per-layer indexer params",
        "The loader expects a DeepSeek-V3.2-style indexer on every layer, but GLM-5.2's IndexShare places them on a subset. mlx-community/GLM-5.2-mxfp4 aborts with 285 missing parameters."),
    "ml-explore/mlx-lm#1572": ("high", ">300GB models trip the GPU watchdog at load",
        "load_model() ends with one mx.eval(model.parameters()), building a single enormous Metal command buffer. At ~390GB it hits kIOGPUCommandBufferCallbackErrorTimeout and the error escapes uncaught, hard-aborting the process. GLM-5.2 at 4-bit is 372-475GB."),

    "waybarrios/vllm-mlx#619": ("high", "Hardcoded mx.set_cache_limit(32GB) is not device-scaled",
        "Filed as an OOM on small Macs, but it cuts the other way here: a hardcoded 32GB ceiling on a 256GB box leaves most of the machine unused."),
    "waybarrios/vllm-mlx#627": ("medium", "memory_budget_gb never reconciled with the Metal allocation ceiling",
        "Two allocators with different ideas of the budget. Relevant when hot-swapping checkpoints for A/B runs."),
    "waybarrios/vllm-mlx#682": ("medium", "Closing a stream leaves the inner generator and request state open",
        "Client disconnects are routine in agentic work; leaked request state accumulates."),
    "waybarrios/vllm-mlx#672": ("high", "Streaming tool calls can end without finish_reason",
        "A tool call that ends without a terminator is exactly the shape that reads as a fabricated turn downstream."),
    "waybarrios/vllm-mlx#546": ("high", "Strict json_schema decode wedges with no token progress",
        "Over 5-minute hangs on Qwen3-Coder-30B-A3B. Structured output is load-bearing for tool arguments."),
    "waybarrios/vllm-mlx#584": ("high", "Non-loopback requests silently dropped on --host 0.0.0.0",
        "Deployment blocker: a server on the LAN is reachable only from localhost. Silent — no log, recv-queue 0."),
    "waybarrios/vllm-mlx#732": ("medium", "PR: surface prefix-cache reuse via usage.prompt_tokens_details.cached_tokens",
        "Observability. Without it there is no way to confirm a hit rate from the API — which is how #730 stayed silent."),
    "ml-explore/mlx-lm#1573": ("medium", "RotatingKVCache.to_quantized() blocks --kv-bits on sliding-window layers",
        "Gemma 4's sliding-window attention cannot use a quantised KV cache."),
    "ml-explore/mlx-lm#1493": ("critical", "Generation hangs at 0% CPU right after prompt processing",
        "A wedge, not a slowdown - the server stops doing work with no error."),
    "ml-explore/mlx-lm#1352": ("high", "Gemma 4 with thinking enabled returns only reasoning, content empty",
        "The visible reply comes back blank whenever thinking is on."),
    "ml-explore/mlx-lm#1242": ("medium", "Error loading mlx-community/gemma-4-e4b-it-4bit",
        "The published small-variant quant does not load cleanly."),
    "waybarrios/vllm-mlx#590": ("medium", "Gemma 4 TextModel dispatch, logit_bias API, and MLLM fallback stalls",
        "Dispatch falls through to qwen3_5 rather than the Gemma path."),
    "waybarrios/vllm-mlx#725": ("medium", "PR: GLM-4.7 thinking streams into content, not reasoning_content",
        "With --reasoning-parser glm4 the entire thinking block lands in content. Non-streaming is unaffected, so it is easy to miss - an agent frontend renders the model's reasoning as the visible reply."),
    "ml-explore/mlx-lm#1401": ("critical", "PR: Add MiniMax-M3 (text backbone) - unmerged",
        "The only route to M3 on MLX, open since 2026-08-24. The only route to M3 on MLX."),
    "waybarrios/vllm-mlx#570": ("medium", "Qwen3.6-35B-A3B dequantize shape mismatch (works in mlx-vlm)",
        "Same class as mlx-lm #1197: mlx-vlm handles a checkpoint the mlx-lm path does not."),
}

MODELS = [
    {"id": "glm47", "w": 198.6, "est": False, "name": "GLM-4.7", "verdict": "ready", "verdict_label": "Recommended",
     "arch": "MoE 358B total / ~32B active · conventional attention", "lic": "MIT", "ctx": "131k",
     "quant": ("mlx-community/GLM-4.7-4bit", 198.6, "39 shards"),
     "alt": [("mlx-community/GLM-4.7-6bit", 286.7, "exceeds one box")],
     "vram": "~209 GB resident · leaves ~21 GB for KV at a 230 GB wired limit",
     "vram_tight": True,
     "hf": "zai-org/GLM-4.7",
     "coding": [("SWE-bench Verified", "73.8%"), ("LiveCodeBench-v6", "84.9%"), ("SWE-bench Multilingual", "66.7%")],
     "agentic": [("τ²-Bench", "87.4%"), ("BrowseComp", "67.5%"), ("Terminal-Bench 2.0", "41.0%")],
     "srcs": [("Model card (all scores)", "https://huggingface.co/zai-org/GLM-4.7")],
     "note": "The strongest model that fits a single 256 GB machine without heroics, MIT-licensed, and the only one on this page that every engine here can load. What varies is the fit: llama.cpp reaches a 158.7 GB Q3 tier while the MLX 4-bit is 198.6 GB, which on one box is the difference between a usable context and a token budget. It uses conventional attention rather than hybrid linear attention, which is why it avoids the class of cache bug that dogs Qwen3.8-27B.",
     "items": ["waybarrios/vllm-mlx#725"]},
    {"id": "glm47f", "w": 16.9, "est": False, "name": "GLM-4.7-Flash", "verdict": "ready", "verdict_label": "Fast lane",
     "arch": "MoE 31B total / ~3B active", "lic": "MIT", "ctx": "131k",
     "quant": ("mlx-community/GLM-4.7-Flash-4bit", 16.9, "4 shards"),
     "alt": [("mlx-community/GLM-4.7-Flash-6bit", 24.3, "also comfortable")],
     "vram": "~27 GB resident · leaves ~203 GB for KV",
     "hf": "zai-org/GLM-4.7-Flash",
     "coding": [("SWE-bench Verified", "59.2%"), ("LiveCodeBench-v6", "64.0%")],
     "agentic": [("τ²-Bench", "79.5%"), ("BrowseComp", "42.8%")],
     "srcs": [("Model card (all scores)", "https://huggingface.co/zai-org/GLM-4.7-Flash")],
     "note": "3B active, so decode is bandwidth-cheap and KV space is abundant - the opposite tradeoff to GLM-4.7 from the same family and the same license. The natural cheap tier to route low-stakes work to, and the easiest thing on this page to get running on any engine.",
     "items": ["waybarrios/vllm-mlx#725"]},
    {"id": "glimmer", "name": "Muse Glimmer 30B", "verdict": "ready", "verdict_label": "Recommended",
     "w": 19.4, "est": False,
     "arch": "Dense 30B \u00b7 multimodal (text + image)", "lic": "Apache-2.0", "ctx": "131k",
     "quant": ("mlx-community/Muse-Glimmer-30B-4bit", 19.4, "4 shards"),
     "alt": [("mlx-community/Muse-Glimmer-30B-8bit", 32.4, "headroom to spare either way")],
     "vram": "~29 GB resident \u00b7 leaves ~201 GB for KV on a 256 GB machine",
     "hf": "meta-models/Muse-Glimmer-30B",
     "coding": [("SWE-bench Verified", "76.0"), ("SWE-bench Pro", "51.2")],
     "agentic": [("MCP Atlas", "75.5"), ("DeepSearch QA", "74.6"), ("OSWorld-Verified", "65.9"), ("GAIA2", "43.3"), ("Terminal-Bench 2.1", "51.7")],
     "srcs": [("Meta AI Research announcement", "https://research.meta.ai/blog/introducing-muse-glimmer-open-agentic-model"),
              ("Artificial Analysis benchmarks", "https://artificialanalysis.ai/articles/muse-glimmer"),
              ("Model card", "https://huggingface.co/meta-models/Muse-Glimmer-30B")],
     "note": "Meta's open agentic model, distilled from the closed Muse Spark - Spark itself is API-only, so this is the one you can actually run. Apache-2.0, with Meta publishing both the GGUF and a draft head, and mlx-community carrying a 4/5/6/8-bit family. It leads MCP Atlas at 75.5 and posts SWE-bench Verified 76.0, but its Terminal-Bench 2.1 of 51.7 trails Qwen3.8-27B's 73.0, so it is stronger at tool orchestration than at raw terminal work. One caution for agent use: Siren AgentDojo puts its prompt-injection attack-success rate at 28.4%.",
     "items": []},
    {"id": "nemolight", "name": "Nemotron 3.5 Lightning", "verdict": "ready", "verdict_label": "Fast lane",
     "w": 17.8, "est": False,
     "arch": "MoE 30B total / ~3B active \u00b7 hybrid Mamba-Transformer", "lic": "NVIDIA OpenMDW-1.1", "ctx": "128k",
     "quant": ("mlx-community/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-4bit", 17.8, "4 shards"),
     "alt": [],
     "vram": "~28 GB resident \u00b7 leaves ~202 GB for KV on a 256 GB machine",
     "hf": "nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B",
     "coding": [("SWE-bench Verified", "51.56"), ("PinchBench", "85.37")],
     "agentic": [("MMLU Pro", "81.94"), ("GPQA Diamond", "75.44")],
     "srcs": [("NVIDIA model card", "https://build.nvidia.com/nvidia/nemotron-3.5-lightning-30b-a3b/modelcard"),
              ("Benchmark writeup", "https://www.datacamp.com/blog/nemotron-3-5-lightning")],
     "note": "Released 2026-08-11 with weights, training data and recipes. 3B active makes it the cheapest thing here to run at concurrency, and the checkpoint ships MTP draft weights. Published agentic coverage is thin - NVIDIA leads with general benchmarks - so treat it as a fast tier to trial rather than a proven agentic pick. The larger Nemotron 3 Super (120B-A12B) and Ultra (550B-A55B, SWE-bench Verified 70.7) are stronger but have no Apple-ready quantisation published.",
     "items": []},
    {"id": "gptoss", "name": "gpt-oss-120b", "verdict": "ready", "verdict_label": "Solid",
     "w": 65.8, "est": False,
     "arch": "MoE 120B total / ~5.1B active", "lic": "Apache-2.0", "ctx": "128k",
     "quant": ("mlx-community/gpt-oss-120b-4bit", 65.8, "13 shards"),
     "alt": [],
     "vram": "~76 GB resident \u00b7 leaves ~154 GB for KV on a 256 GB machine",
     "hf": "openai/gpt-oss-120b",
     "coding": [("SWE-bench Verified (high)", "62.4%"), ("Codeforces", "2622 Elo")],
     "agentic": [("\u03c4-Bench Retail (high)", "67.8%"), ("\u03c4-Bench Airline (high)", "49.2%")],
     "srcs": [("Model card / paper", "https://arxiv.org/html/2508.10925v1"),
              ("OpenAI announcement", "https://openai.com/index/introducing-gpt-oss/")],
     "note": "Older now, but a genuinely comfortable fit on any engine: 5.1B active means fast decode and 63-66 GB leaves plenty of KV room. Scores scale with reasoning effort - the figures shown are the high setting; medium gives SWE-bench 52.6% and τ-Bench Retail 62.0%. Apache-2.0. Its one recurring problem is not the model but Harmony: the channel format its tool calls ride on has open parsing defects in more than one engine.",
     "items": []},
    {"id": "gemma4", "name": "Gemma 4 31B", "verdict": "blocked", "verdict_label": "Blocked",
     "w": 17.5, "est": True,
     "arch": "Dense 30.7B \u00b7 also E2B / E4B / 26B-A4B variants", "lic": "Apache-2.0", "ctx": "256k",
     "quant": (None, 0, "no 4-bit MLX quant published for the 31B"),
     "alt": [],
     "vram": "~18 GB estimated at 4-bit, if a quant existed",
     "vram_tight": True,
     "hf": "google/gemma-4-31b-it",
     "coding": [("SWE-bench Verified", "52.0%"), ("LiveCodeBench-v6", "80.0%"), ("SWE-bench Pro", "35.7%")],
     "agentic": [("\u03c4\u00b2-Bench", "86.4%")],
     "srcs": [("Benchmark writeup", "https://codersera.com/blog/gemma-4-complete-guide-2026/"),
              ("SWE-bench detail", "https://www.gemma4.wiki/benchmark/gemma-4-swe-bench")],
     "note": "The clearest case on this page for looking past MLX. τ²-Bench 86.4% is the second-highest tool-use number here, Google publishes a quantisation-aware-trained q4_0 GGUF itself at 17.7 GB, and llama.cpp, Ollama and LM Studio all load it today. The MLX side is the worst on this page - no 4-bit quant of the 31B, and more open mlx-lm issues than any other architecture tracked - which is exactly the sort of gap that makes an MLX-only view of Apple Silicon misleading.",
     "items": ["ml-explore/mlx-lm#1493", "ml-explore/mlx-lm#1352", "ml-explore/mlx-lm#1242",
               "waybarrios/vllm-mlx#590", "ml-explore/mlx-lm#1573"]},
    {"id": "qwen38", "w": 20.7, "est": False, "name": "Qwen3.8-27B", "verdict": "degraded", "verdict_label": "Runs, degraded",
     "arch": "Dense 27.8B · hybrid GDN (48 linear + 16 full-attn)", "lic": "Apache-2.0", "ctx": "262k (to 1M)",
     "quant": ("mlx-community/Qwen3.8-27B-OptiQ-4bit", 20.7, "6 shards"),
     "alt": [("mlx-community/Qwen3.8-27B-8bit", 29.5, "the build used in vllm-mlx #730")],
     "vram": "~31 GB resident · leaves ~199 GB for KV",
     "hf": "Qwen/Qwen3.8-27B",
     "coding": [("LiveCodeBench-v6", "90.3"), ("QwenSWEBench", "79.0"), ("SWE-bench Pro", "61.7"), ("DeepSWE 1.1", "42.2")],
     "agentic": [("Terminal-Bench 2.1", "73.0"), ("OSWorld (computer use)", "84.3"), ("AndroidWorld", "81.9"), ("WebArena", "64.8")],
     "srcs": [("Model card (all scores)", "https://huggingface.co/Qwen/Qwen3.8-27B")],
     "note": "Stronger on paper than its size suggests: LiveCodeBench-v6 of 90.3 beats GLM-4.7's 84.9, and SWE-bench Pro of 61.7 is within noise of GLM-5.2's 62.1 at 1/27th the scale. Its hybrid Gated DeltaNet layout is also the most engine-sensitive thing here - the same weights get working multi-token speculative decoding on one engine and a k=1 cap on another, so which runtime you pick changes the throughput more than which quant you pick.",
     "items": ["waybarrios/vllm-mlx#730", "waybarrios/vllm-mlx#731", "waybarrios/vllm-mlx#710",
               "ml-explore/mlx-lm#1446", "waybarrios/vllm-mlx#678", "waybarrios/vllm-mlx#641",
               "waybarrios/vllm-mlx#711", "waybarrios/vllm-mlx#729", "waybarrios/vllm-mlx#689",
               "waybarrios/vllm-mlx#658"]},
    {"id": "m3", "w": 215.0, "est": True, "name": "MiniMax M3", "verdict": "blocked", "verdict_label": "Blocked",
     "arch": "MoE 428B total / 23B active · MiniMax Sparse Attention",
     "lic": "MiniMax Community", "ctx": "1M",
     "quant": (None, 0, "no MLX quant - support unmerged"),
     "alt": [],
     "vram": "~215 GB estimated at 4-bit · would leave ~5 GB for KV",
     "vram_tight": True,
     "hf": "MiniMaxAI/MiniMax-M3",
     "coding": [("SWE-bench Verified", "80.5%"), ("SWE-bench Pro", "59.0%"), ("SWE-fficiency", "34.8")],
     "agentic": [("Terminal-Bench 2.1", "66.0"), ("MCP Atlas", "74.2")],
     "srcs": [("Model card", "https://huggingface.co/MiniMaxAI/MiniMax-M3"),
              ("Benchmark writeup", "https://www.morphllm.com/minimax-m3")],
     "note": "SWE-bench Verified 80.5% is the best coding score on this page that fits one 256 GB machine, and since the architecture reached mainline llama.cpp that is now a real option rather than a hypothetical. Note its Terminal-Bench 2.1 of 66.0 sits below Qwen3.8-27B's 73.0 despite being 15x larger, so it is a coding pick rather than an agentic one. The MLX route is a vision-language checkpoint with open loader problems.",
     "items": ["ml-explore/mlx-lm#1401"]},
    {"id": "v4flash", "w": 151.3, "est": False, "name": "DeepSeek V4 Flash", "verdict": "blocked", "verdict_label": "Blocked",
     "arch": "MoE 284B total / 13B active · DSA sparse attention", "lic": "MIT", "ctx": "1M",
     "quant": ("mlx-community/DeepSeek-V4-Flash-mxfp4", 151.3, "33 shards"),
     "alt": [],
     "vram": "~161 GB resident · would leave ~69 GB for KV",
     "hf": "deepseek-ai/DeepSeek-V4-Flash",
     "coding": [("SWE-bench Verified", "not published")],
     "agentic": [("AA Intelligence Index", "50"), ("GDPval-AA max effort", "1388")],
     "srcs": [("Artificial Analysis writeup", "https://artificialanalysis.ai/articles/deepseek-is-back-among-the-leading-open-weights-models-with-v4-pro-and-v4-flash")],
     "note": "The best shape on this page for Apple hardware: 13B active reads roughly 7.5 GB per token, so bandwidth stops being the constraint and a 256 GB machine finally does useful work. It is also the clearest example of a model whose story depends entirely on the engine - unreachable through the mainstream MLX servers, and the fastest thing here through the engine written specifically for it.",
     "items": ["waybarrios/vllm-mlx#668", "ml-explore/mlx-lm#1332", "ml-explore/mlx-lm#1443"]},
    {"id": "glm52", "w": 395.1, "est": False, "name": "GLM-5.2", "verdict": "blocked", "verdict_label": "Blocked",
     "arch": "MoE 744B total / 40B active · glm_moe_dsa + IndexShare", "lic": "MIT", "ctx": "1M",
     "quant": ("mlx-community/GLM-5.2-mxfp4", 395.1, "76 shards"),
     "alt": [],
     "vram": "~405 GB resident · pooled across both machines only",
     "vram_tight": True,
     "hf": "zai-org/GLM-5.2",
     "coding": [("SWE-bench Pro", "62.1%"), ("DeepSWE", "46.2"), ("AIME 2026", "99.2")],
     "agentic": [("Terminal-Bench 2.1", "81.0")],
     "srcs": [("Artificial Analysis writeup", "https://artificialanalysis.ai/articles/glm-5-2-is-the-new-leading-open-weights-model-on-the-artificial-analysis-intelligence-index"),
              ("Model card", "https://huggingface.co/zai-org/GLM-5.2")],
     "note": "The highest agentic score reachable on Apple hardware, and reachable today - just not through the MLX servers, which are blocked three ways. The practical constraints are size and precision: the builds that fit one or two Macs are 1-2 bit, so the honest question is not whether it loads but how much of the model survives the quantisation.",
     "items": ["ml-explore/mlx-lm#1418", "ml-explore/mlx-lm#1443", "ml-explore/mlx-lm#1572"]},
    {"id": "v4pro", "name": "DeepSeek V4 Pro", "verdict": "blocked", "verdict_label": "Blocked",
     "w": 800.0, "est": True,
     "arch": "MoE 1.6T total / 49B active · DSA sparse attention", "lic": "MIT", "ctx": "1M",
     "quant": (None, 0, "no MLX quant published"),
     "alt": [],
     "vram": "~800 GB estimated at 4-bit",
     "hf": "deepseek-ai/DeepSeek-V4-Pro",
     "coding": [("SWE-bench Verified", "80.6%")],
     "agentic": [("GDPval-AA", "1554")],
     "srcs": [("Artificial Analysis writeup", "https://artificialanalysis.ai/articles/deepseek-is-back-among-the-leading-open-weights-models-with-v4-pro-and-v4-flash")],
     "note": "Same architecture as Flash at roughly five times the size, which makes it a capacity problem rather than a compatibility one. It runs, on hardware most people will not have: a 512 GB machine, or a pair of them for the Q4 split. Worth knowing it exists so you can price the ceiling.",
     "items": ["waybarrios/vllm-mlx#668", "ml-explore/mlx-lm#1443"]},
    {"id": "kimik3", "name": "Kimi K3", "verdict": "blocked", "verdict_label": "Blocked",
     "w": 1400.0, "est": True,
     "arch": "MoE 2.8T total / 104B active", "lic": "Modified MIT", "ctx": "1M",
     "quant": (None, 0, "no MLX quant published"),
     "alt": [],
     "vram": "~1.4 TB estimated at 4-bit",
     "hf": "moonshotai/Kimi-K3",
     "coding": [("LiveBench Coding", "81.45"), ("Agentic Coding", "57.58")],
     "agentic": [("Terminal-Bench 2.1", "88.3"), ("MCPMark-Verified", "94.5"), ("OSWorld-Verified", "84.8")],
     "srcs": [("Benchmark roundup", "https://www.morphllm.com/best-open-source-llm")],
     "note": "The best open-weight agentic model there is - Terminal-Bench 2.1 of 88.3, MCPMark-Verified 94.5 - and the hardest to get onto a Mac. Both available routes trade quality for fit: 1-bit GGUF tiers on one side, community expert-pruned MLX builds on the other. Neither is the model the benchmarks describe, and the honest position is that nobody has published Apple-hardware evaluations of either.",
     "items": []},
    {"id": "qcnext", "name": "Qwen3-Coder-Next", "w": 18.9, "est": False,
     "arch": "MoE 80B total / 3B active \u00b7 12 Gated Attention + 36 Gated DeltaNet layers",
     "lic": "Apache-2.0", "ctx": "262k",
     "hf": "Qwen/Qwen3-Coder-Next",
     "coding": [("SWE-bench Verified", "74.2%"), ("SWE-bench Multilingual", "63.7%"), ("Aider", "66.2")],
     "agentic": [("Terminal-Bench 2.0", "36.2")],
     "srcs": [("Model card", "https://huggingface.co/Qwen/Qwen3-Coder-Next"),
              ("Qwen blog", "https://qwen.ai/blog?id=qwen3-coder-next")],
     "note": "The best fit-to-capability ratio on this page. 3B active out of 80B total gets SWE-bench Verified "
             "74.2% - within a couple of points of GLM-4.7 at a quarter the footprint - and Apache-2.0 with a "
             "38-tier GGUF ladder means it runs on almost anything. Note the caveats: its Terminal-Bench figure "
             "is on v2.0, so it cannot be ranked against the v2.1 numbers elsewhere here, and it is "
             "non-thinking only. KV is 24 KiB/token, among the cheapest here, so long context is affordable."},
    {"id": "q38fnext", "name": "Qwen3.8-Flash-Next", "w": 72.5, "est": False,
     "arch": "MoE 125B + 51B n-gram embedding / 6B active \u00b7 Gated DeltaNet + Qwen Sparse Attention",
     "lic": "Qwen Community 1.0", "ctx": "262k (1M on the hosted version)",
     "hf": "Qwen/Qwen3.8-Flash-Next",
     "coding": [("SWE-bench Multilingual", "81.0"), ("SWE-bench Pro", "62.5"),
                ("LiveCodeBench v6", "91.9"), ("DeepSWE 1.1", "58.7")],
     "agentic": [("Toolathlon Verified", "73.5"), ("CoWorkBench", "73.9"), ("JobBench", "55.7"),
                 ("Agents\u2019 Last Exam", "24.3")],
     "srcs": [("Model card with full tables", "https://huggingface.co/Qwen/Qwen3.8-Flash-Next"),
              ("Qwen blog", "https://qwen.ai/blog?id=qwen3.8-flash-next")],
     "note": "Qwen calls this an experimental preview of the architecture behind Qwen4, and the numbers are "
             "the strongest per active parameter on this page: 6B active beats Qwen3.8-27B on every shared "
             "benchmark, and its SWE-bench Multilingual of 81.0 leads the page outright. Three genuinely new "
             "pieces - Qwen Sparse Attention at micro-block granularity, gated residuals, and a 51B n-gram "
             "embedding table designed to be offloaded. That last one is why the checkpoint is 180B on disk "
             "against a stated 125B. None of it runs on Apple silicon yet: the architecture is `qwen4_exp` and "
             "no runtime here implements it."},
    {"id": "qwenmax", "name": "Qwen3.8-Max", "w": 246.2, "est": False,
     "arch": "MoE 2.45T total / 95B active \u00b7 hybrid GDN (23 full-attn + 69 linear of 92)",
     "lic": "Qwen3.8-Max (custom)", "ctx": "262k",
     "hf": "Qwen/Qwen3.8-2.4T-A95B",
     "coding": [("SWE-bench Pro", "67.7"), ("QwenSWEBench", "80.7"), ("FrontierSWE", "73.5"),
                ("DeepSWE 1.1", "56.6")],
     "agentic": [("Terminal-Bench 2.1", "86.6"), ("CoWorkBench", "74.8"),
                 ("Toolathlon Verified", "72.5"), ("JobBench", "53.4")],
     "srcs": [("Model card with full tables", "https://huggingface.co/Qwen/Qwen3.8-2.4T-A95B")],
     "note": "The weights are public at Qwen/Qwen3.8-2.4T-A95B and the architecture is already supported - "
             "this is the same qwen3_5_moe family as Qwen3.8-27B, so llama.cpp and mlx-lm both load it. "
             "Terminal-Bench 2.1 of 86.6 is second only to Kimi K3 on this page, and its SWE-bench Pro of 67.7 "
             "leads it outright. What stops it is arithmetic: 2.45T parameters means the smallest unpruned "
             "build is 397 GB at 1.30 bits per weight, and the first tier clearing 2 bits is 656 GB. Everything "
             "that fits a realistic Mac has either been quantised past the point its own quantiser warns "
             "about, or had most of its experts deleted."},
]

META.update(EMETA)

PR_KEYS = {"waybarrios/vllm-mlx#731", "waybarrios/vllm-mlx#732", "waybarrios/vllm-mlx#729",
           "waybarrios/vllm-mlx#725", "ml-explore/mlx-lm#1401", "ml-explore/mlx-lm#1233"}

# works/degraded/blocked/none -> the CSS verdict classes the page already uses
SCLASS = {"works": "ready", "degraded": "degraded", "blocked": "blocked", "none": "unknown"}

CROSS = ["waybarrios/vllm-mlx#619", "waybarrios/vllm-mlx#584", "waybarrios/vllm-mlx#672",
         "waybarrios/vllm-mlx#546", "waybarrios/vllm-mlx#627", "waybarrios/vllm-mlx#682",
         "waybarrios/vllm-mlx#732", "waybarrios/vllm-mlx#570"]

SEV_LABEL = {"critical": "Critical", "high": "High", "medium": "Medium", "low": "Low"}
SEV_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def read_state():
    rows, releases = {}, {}
    if not os.path.exists(STATE):
        return rows, releases
    for line in open(STATE):
        line = line.strip()
        if not line or "|" not in line:
            continue
        key, state, _label = (line.split("|", 2) + ["", ""])[:3]
        if key.endswith("@release"):
            releases[key[:-len("@release")]] = state
        else:
            rows[key] = state
    return rows, releases


def pill(state):
    s = (state or "open").lower()
    if s == "merged":
        return "merged", "Merged"
    if s == "closed":
        return "closed", "Closed"
    return "open", "Open"


def issue_url(key):
    repo, num = key.split("#")
    kind = "pull" if key in PR_KEYS else "issues"
    return f"https://github.com/{repo}/{kind}/{num}"


def slug(name):
    return "m-" + "".join(c.lower() if c.isalnum() else "-" for c in name).strip("-")


def best_cell(m):
    """The engine a model card opens on."""
    eid = BEST[m["id"]]
    return eid, MATRIX[m["id"]][eid]


def fam_for(eid, mid):
    return FAM_OVERRIDE.get((eid, mid), FAM[eid])


def ladder_for(eid, mid):
    """Measured rungs this engine can load for this model, largest first."""
    if MATRIX[mid][eid]["s"] == "none":
        return []
    return LADDERS.get(mid, {}).get(fam_for(eid, mid), [])


def engine_payload(m):
    """Every engine that can run this model, with its own quant ladder.

    Ordered by architecture support first, then by whether it is the
    recommended engine - the browser walks this and takes the first entry with a
    rung that fits, so preference only breaks ties between equally-supported
    engines.
    """
    mid = m["id"]
    best = BEST[mid]
    rank = {"ready": 0, "degraded": 1, "blocked": 2, "unknown": 3}
    out = []
    for eid in engine_order(mid):
        c = MATRIX[mid][eid]
        lad = ladder_for(eid, mid)
        if not lad:
            continue
        out.append({"id": eid, "name": ENGINE_BY_ID[eid]["name"], "s": SCLASS[c["s"]],
                    "label": c["label"], "fam": fam_for(eid, mid),
                    "note": FIDELITY_NOTES.get((mid, fam_for(eid, mid)), ""),
                    "ladder": lad})
    out.sort(key=lambda d: (rank[d["s"]], 0 if d["id"] == best else 1,
                            -(d["ladder"][-1]["gb"] if d["ladder"] else 0)))
    return out


def model_payload(m):
    bpt, maxctx, why = KV.get(m["id"], (None, None, ""))
    return {"engines": engine_payload(m),
            "kv": {"bpt": bpt, "maxctx": maxctx, "why": why},
            "params": PARAMS.get(m["id"])}


def index_rows(rows):
    """One line per model. The size, engine and headroom cells are all filled in
    by the browser once a cluster is selected - the server-rendered values are
    just the default-cluster answer so the page is not blank without JS."""
    out = []
    for m in sorted(MODELS, key=lambda m: m["name"].casefold()):
        eid, c = best_cell(m)
        lad = ladder_for(eid, m["id"])
        gb = lad[-1]["gb"] if lad else m["w"]
        payload = html.escape(json.dumps(model_payload(m)), quote=True)
        out.append(f"""
        <a class="ix-row v-{SCLASS[c['s']]}" href="#{m['id']}" data-model="{m['id']}"
           data-sw="{SCLASS[c['s']]}" data-swlabel="{html.escape(c['label'])}" data-payload="{payload}">
          <span class="ix-name">{html.escape(m['name'])}</span>
          <span class="ix-status v-{SCLASS[c['s']]}">{html.escape(c['label'])}</span>
          <span class="ix-eng">{html.escape(ENGINE_BY_ID[eid]['name'])}</span>
          <span class="ix-size">{gb:.0f} GB</span>
          <span class="ix-meta fit"></span>
        </a>""")
    return "".join(out)


def src_links(m):
    out = [f"""<a class="src" href="https://huggingface.co/{m['hf']}" target="_blank" rel="noopener">{html.escape(m['hf'])}</a>"""]
    out += [f"""<a class="src" href="{u}" target="_blank" rel="noopener">{html.escape(lbl)}</a>""" for lbl, u in m["srcs"]]
    return "".join(out)


def scores(pairs):
    return "".join(
        f"""<div class="score"><span class="score-k">{html.escape(k)}</span>"""
        f"""<span class="score-v">{html.escape(v)}</span></div>"""
        for k, v in pairs)


def prose(text):
    """HTML-escape, then render inline `code` spans and [text](url) links."""
    out = re.sub(r"`([^`]+)`", lambda m: f"<code>{m.group(1)}</code>", html.escape(text))
    out = re.sub(r"\*\*([^*]+)\*\*", lambda m: f"<strong>{m.group(1)}</strong>", out)
    return re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
                  lambda m: f'<a href="{m.group(2)}" target="_blank" rel="noopener">{m.group(1)}</a>',
                  out)


API_ROWS = [("endpoints", "Endpoints"), ("streaming", "Streaming"), ("tools", "Tool calling"),
            ("structured", "Structured output"), ("concurrency", "Concurrency"), ("gotcha", "Watch for")]


def api_block(e):
    api = e.get("api_detail")
    if not api:
        return ""
    rows = "".join(
        f"""<div class="api-row"><dt>{html.escape(label)}</dt><dd>{prose(api[k])}</dd></div>"""
        for k, label in API_ROWS if api.get(k))
    return f"""<dl class="api">{rows}</dl>"""


def engine_build(mid, eid):
    """The chosen rung is filled in by the browser; this is the static fallback."""
    lad = ladder_for(eid, mid)
    if not lad:
        c = MATRIX[mid][eid]
        label = c["q"][0] if c.get("q") else "no build published for this engine"
        return f"""<div class="eng-build none"><span class="eng-build-k">Build</span><span>{html.escape(label)}</span></div>"""
    return (f"""<div class="eng-build"><span class="eng-build-k">Build</span>"""
            f"""<a class="build-link" href="#" target="_blank" rel="noopener"></a>"""
            f"""<span class="build-bpw"></span></div>""")


def engine_meta_line(e):
    bits = [("Interface", e["surface"]), ("Format", e["fmt"]), ("API", e["api"]), ("License", e["lic"])]
    return "".join(f"""<div><dt>{html.escape(k)}</dt><dd>{html.escape(v)}</dd></div>""" for k, v in bits)


def engine_tabs(m, rows):
    mid, order = m["id"], engine_order(m["id"])
    tabs, panes = [], []
    for i, eid in enumerate(order):
        c, e = MATRIX[mid][eid], ENGINE_BY_ID[eid]
        sc = SCLASS[c["s"]]
        sel = "true" if i == 0 else "false"
        n_open = sum(1 for k in c["items"] if rows.get(k, "open").lower() == "open")
        tabs.append(f"""
          <button type="button" role="tab" class="eng-tab s-{sc}" data-eng="{eid}"
                  aria-selected="{sel}" aria-controls="{mid}-{eid}" id="{mid}-{eid}-tab">
            <span class="eng-tab-n">{html.escape(e['name'])}</span>
            <span class="eng-tab-s s-{sc}">{html.escape(c['label'])}</span>
          </button>""")
        lad = ladder_for(eid, mid)
        w_attr = ' data-has-ladder="1"' if lad else ""
        items = render_items(c["items"], rows)
        body = (f"""<ul class="rows">{items}\n          </ul>"""
                if items else
                """<p class="eng-clear">Nothing open tracked against this engine for this model.</p>""")
        # A blocked engine cannot load the model at all, so quoting a build, a
        # resident size, a fidelity band or a context table for it is noise at
        # best and misleading at worst. Leave the reason and the issues.
        sizing = "" if c["s"] in ("blocked", "none") else f"""
          {engine_build(mid, eid)}
          <div class="eng-fit s-{sc}"{w_attr}></div>
          <p class="fidelity" hidden></p>
          <div class="ctx-wrap" hidden><span class="ctx-k">Concurrent contexts in the KV headroom</span>
            <table class="ctx"><thead><tr><th>Context each</th><th>KV per stream</th><th>Streams</th></tr></thead>
            <tbody></tbody></table>
            <p class="ctx-why"></p></div>"""
        panes.append(f"""
        <div class="eng-pane" id="{mid}-{eid}" role="tabpanel" aria-labelledby="{mid}-{eid}-tab"
             data-eng="{eid}"{'' if i == 0 else ' hidden'}>
          <dl class="eng-meta">{engine_meta_line(e)}</dl>{sizing}
          <p class="eng-note">{prose(c['note'])}</p>
          <p class="blockers-label">{n_open} open of {len(c['items'])} tracked on this engine</p>
          {body}
        </div>""")
    return f"""
      <div class="eng" data-model="{mid}">
        <div class="eng-tabs" role="tablist" aria-label="Engines for {html.escape(m['name'])}">{''.join(tabs)}
        </div>{''.join(panes)}
      </div>"""


def cross_tabs(rows, releases):
    feeds = {f["engine"]: f for f in RELEASE_FEEDS}
    tabs, panes = [], []
    for i, e in enumerate(ENGINES):
        eid = e["id"]
        keys = CROSS_BY_ENGINE.get(eid, [])
        n_open = sum(1 for k in keys if rows.get(k, "open").lower() == "open")
        sel = "true" if i == 0 else "false"
        tabs.append(f"""
          <button type="button" role="tab" class="eng-tab" data-eng="{eid}"
                  aria-selected="{sel}" aria-controls="cross-{eid}" id="cross-{eid}-tab">
            <span class="eng-tab-n">{html.escape(e['name'])}</span>
            <span class="eng-tab-s">{n_open} open</span>
          </button>""")
        items = render_items(keys, rows)
        body = (f"""<ul class="cross-list">{items}\n          </ul>""" if items else
                """<p class="eng-clear">Nothing server-wide tracked against this engine.</p>""")
        panes.append(f"""
        <div class="eng-pane" id="cross-{eid}" role="tabpanel" aria-labelledby="cross-{eid}-tab"
             data-eng="{eid}"{'' if i == 0 else ' hidden'}>
          <dl class="eng-meta">{engine_meta_line(e)}{release_cell(feeds.get(eid), releases)}</dl>
          <p class="eng-note">{prose(e['what'])}</p>
          {api_block(e)}
          {body}
        </div>""")
    return f"""
      <div class="eng" data-model="cross">
        <div class="eng-tabs" role="tablist" aria-label="Engines">{''.join(tabs)}
        </div>{''.join(panes)}
      </div>"""


def release_cell(feed, releases):
    """The engine's latest release, shown alongside its other facts."""
    if not feed:
        return ""
    if feed["scheme"] == "none":
        tag = "no tag feed"
    else:
        tag = releases.get(feed["repo"], "not seen yet")
    note = f" &middot; {html.escape(feed['note'])}" if feed["note"] else ""
    return (f"""<div><dt>Latest release</dt><dd>{html.escape(tag)}"""
            f"""<span class="rel-note">{note}</span></dd></div>""")


def release_rows(releases):
    out = []
    for f in RELEASE_FEEDS:
        e = ENGINE_BY_ID[f["engine"]]
        repo = f["repo"]
        name = (f"""<a href="https://github.com/{repo}" target="_blank" rel="noopener">{html.escape(e['name'])}</a>"""
                if repo else html.escape(e["name"]))
        tag = "no tag feed" if f["scheme"] == "none" else releases.get(repo, "not seen yet")
        note = f"""<span class="rel-note">{html.escape(f['note'])}</span>""" if f["note"] else ""
        out.append(f"""<div class="rel"><span class="rel-repo">{name}{note}</span>"""
                   f"""<span class="rel-tag">{html.escape(tag)}</span></div>""")
    return "".join(out)


def render_items(keys, rows):
    present = [k for k in keys if k in META]
    present.sort(key=lambda k: (SEV_ORDER.get(META[k][0], 9), k))
    out = []
    for key in present:
        sev, headline, why = META[key]
        state = rows.get(key, "open")
        cls, txt = pill(state)
        repo, num = key.split("#")
        short = repo_label(key)
        out.append(f"""
        <li class="row sev-{sev}">
          <div class="row-head">
            <a class="ref" href="{issue_url(key)}" target="_blank" rel="noopener">{short}&thinsp;#{num}</a>
            <span class="pill {cls}">{txt}</span>
            <span class="sev-tag">{SEV_LABEL[sev]}</span>
          </div>
          <h4>{html.escape(headline)}</h4>
          <p>{prose(why)}</p>
        </li>""")
    return "".join(out)


def render():
    rows, releases = read_state()
    stamp = datetime.datetime.now().astimezone()
    now = stamp.strftime("%Y-%m-%d %H:%M")
    now_iso = stamp.isoformat(timespec="seconds")

    cards = []
    for m in MODELS:
        eid, c = best_cell(m)
        sc = SCLASS[c["s"]]
        payload = html.escape(json.dumps(model_payload(m)), quote=True)
        cards.append(f"""
    <section class="model v-{sc}" id="{m['id']}" data-model="{m['id']}" data-sw="{sc}"
             data-swlabel="{html.escape(c['label'])}" data-payload="{payload}">
      <div class="model-head">
        <div class="model-id">
          <h2>{html.escape(m['name'])}</h2>
          <span class="verdict v-{sc}">{html.escape(c['label'])}</span>
        </div>
        <dl class="spec">
          <div><dt>Architecture</dt><dd>{html.escape(m['arch'])}</dd></div>
          <div><dt>License</dt><dd>{html.escape(m['lic'])}</dd></div>
          <div><dt>Context</dt><dd>{html.escape(m['ctx'])}</dd></div>
        </dl>
        <p class="model-fit"></p>
        <p class="model-note">{prose(m['note'])}</p>
        <div class="srcs"><span class="q-cat">Sources</span>{src_links(m)}</div>
        <details class="scores-wrap">
          <summary>Benchmark scores</summary>
          <div class="scores">
            <div class="score-col"><span class="score-cat">Agentic</span>{scores(m['agentic'])}</div>
            <div class="score-col"><span class="score-cat">Coding</span>{scores(m['coding'])}</div>
          </div>
        </details>
      </div>
      {engine_tabs(m, rows)}
    </section>""")

    # Serialised here rather than baked into TEMPLATE: a frozen literal silently
    # went stale once already when new models were added to USE_CASES.
    usecases = json.dumps([{"id": u["id"], "label": u["label"], "gate": u["gate"],
                            "axis": u["axis"],
                            "rank": [[r[0], r[1], r[2]] for r in u["rank"]]}
                           for u in USE_CASES])
    bands = json.dumps([[b[0], b[1], b[2], b[3]] for b in BANDS])

    doc = TEMPLATE.format(now=now, now_iso=now_iso, usecases=usecases, bands=bands,
                          cards="".join(cards), index=index_rows(rows),
                          cross=cross_tabs(rows, releases))
    return doc.replace("/apple-llm-performance/card.jpg",
                       "/apple-llm-performance/" + card_name())


TEMPLATE = """<title>Apple LLM Performance Tracker</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Open weight AI models and their Apple M-series compatibility.">
<meta property="og:type" content="website">
<meta property="og:site_name" content="DreamingWell">
<meta property="og:url" content="https://dreamingwell.github.io/apple-llm-performance/">
<meta property="og:title" content="Apple LLM Performance Tracker">
<meta property="og:description" content="Open weight AI models and their Apple M-series compatibility.">
<meta property="og:image" content="https://dreamingwell.github.io/apple-llm-performance/card.jpg">
<meta property="og:image:type" content="image/jpeg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Dark card over a glowing Apple Silicon die reading Can Your Mac Run It? - find the best LLM for your Mac, updated daily. Open source on GitHub.">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Apple LLM Performance Tracker">
<meta name="twitter:description" content="Open weight AI models and their Apple M-series compatibility.">
<meta name="twitter:image" content="https://dreamingwell.github.io/apple-llm-performance/card.jpg">
<meta name="twitter:image:alt" content="Dark card over a glowing Apple Silicon die reading Can Your Mac Run It? - find the best LLM for your Mac, updated daily. Open source on GitHub.">
<link rel="canonical" href="https://dreamingwell.github.io/apple-llm-performance/">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap">
<style>
  :root {{
    --bg: #eef1f5; --surface: #ffffff; --surface-2: #f6f8fa;
    --ink: #141a20; --ink-2: #3d4854; --muted: #5f6b78;
    --line: #d9e0e8; --line-soft: #e8edf2;
    --accent: #a85a26;
    --critical: #a8352a; --high: #8a5410; --medium: #4a6070; --low: #78838f;
    --ok: #25704e; --ok-tint: #e8f5ee; --warn: #8a5410;
  }}
  @media (prefers-color-scheme: dark) {{
    :root:not([data-theme="light"]) {{
      --bg: #0e1216; --surface: #161c22; --surface-2: #1b232a;
      --ink: #e3e8ee; --ink-2: #b9c3cd; --muted: #8894a2;
      --line: #29333d; --line-soft: #202932;
      --accent: #de8a4c;
      --critical: #ef7565; --high: #ddb24f; --medium: #7f97a8; --low: #6d7883;
      --ok: #59bc88; --ok-tint: #12251c; --warn: #ddb24f;
    }}
  }}
  :root[data-theme="dark"] {{
    --bg: #0e1216; --surface: #161c22; --surface-2: #1b232a;
    --ink: #e3e8ee; --ink-2: #b9c3cd; --muted: #8894a2;
    --line: #29333d; --line-soft: #202932;
    --accent: #de8a4c;
    --critical: #ef7565; --high: #ddb24f; --medium: #7f97a8; --low: #6d7883;
    --ok: #59bc88; --ok-tint: #12251c; --warn: #ddb24f;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; background: var(--bg); color: var(--ink);
    font-family: "IBM Plex Sans", -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
    font-size: 16px; line-height: 1.55; -webkit-font-smoothing: antialiased;
  }}
  .wrap {{ max-width: 64rem; margin: 0 auto; padding: 3rem 1.5rem 5rem; }}
  header {{ display: flex; flex-direction: column; gap: .5rem; margin-bottom: 2rem; }}
  .eyebrow {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .72rem;
    letter-spacing: .13em; text-transform: uppercase; color: var(--accent); font-weight: 600; }}
  h1 {{ font-size: clamp(1.7rem, 4vw, 2.3rem); font-weight: 700; margin: 0;
    letter-spacing: -.02em; text-wrap: balance; }}
  .sub {{ color: var(--muted); margin: 0; max-width: 48rem; }}
  html {{ scroll-behavior: smooth; }}
  @media (prefers-reduced-motion: reduce) {{ html {{ scroll-behavior: auto; }} }}
  #rig-sentinel {{ height: 1px; margin: 0; }}
  .rig {{ background: var(--surface); border: 1px solid var(--line); border-radius: 10px;
    padding: 1.1rem 1.3rem; margin: 0 0 1.25rem;
    position: sticky; top: 0; z-index: 30; }}
  /* Once it detaches, drop the prose and the rounded top so it reads as a bar
     rather than a card that has escaped. */
  .rig.stuck {{ border-radius: 0 0 10px 10px; border-top-color: transparent;
    box-shadow: 0 6px 18px -8px rgba(0,0,0,.35); padding: .7rem 1.3rem; }}
  .rig.stuck .rig-out, .rig.stuck .rig-warn {{ display: none; }}
  .rig.stuck .rig-controls {{ align-items: center; }}
  @media (prefers-color-scheme: dark) {{
    :root:not([data-theme="light"]) .rig.stuck {{ box-shadow: 0 6px 18px -8px rgba(0,0,0,.7); }}
  }}
  :root[data-theme="dark"] .rig.stuck {{ box-shadow: 0 6px 18px -8px rgba(0,0,0,.7); }}
  .rig select optgroup {{ font-weight: 600; }}
  .rig-controls {{ display: flex; gap: 1.1rem; flex-wrap: wrap; align-items: flex-end; }}
  .rig-f {{ display: flex; flex-direction: column; gap: .28rem; min-width: 0; }}
  .rig-f > span {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .64rem;
    letter-spacing: .1em; text-transform: uppercase; color: var(--muted); font-weight: 600; }}
  .rig select {{ font-family: inherit; font-size: .88rem; font-weight: 500; color: var(--ink);
    background: var(--surface-2); border: 1px solid var(--line); border-radius: 6px;
    padding: .4rem .6rem; min-width: 8.5rem; }}
  .rig select:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 1px; }}
  .rig-out {{ margin: .9rem 0 0; font-size: .87rem; color: var(--ink-2); font-variant-numeric: tabular-nums; }}
  .rig-out strong {{ color: var(--ink); font-weight: 600; }}
  .rig-warn {{ margin: .5rem 0 0; font-size: .8rem; color: var(--critical);
    border-left: 2px solid var(--critical); padding-left: .6rem; }}
  .ix-status.v-toolarge {{ color: var(--low); border-color: var(--line); }}
  .ix-row.v-toolarge {{ border-left-color: var(--low); opacity: .78; }}
  .verdict.v-toolarge {{ color: var(--low); border-color: var(--line); background: var(--surface-2); }}
  .model.v-toolarge .model-head {{ border-top-color: var(--low); }}
  .index {{ margin: 0 0 2.75rem; }}
  .ix-top {{ display: flex; flex-direction: column; align-items: flex-start; gap: .5rem;
    margin-bottom: .85rem; }}
  .uc-f {{ display: flex; align-items: baseline; gap: .5rem; }}
  .uc-f > span {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .64rem;
    letter-spacing: .1em; text-transform: uppercase; color: var(--muted); font-weight: 600; }}
  .uc-f select {{ font-family: inherit; font-size: .84rem; font-weight: 500; color: var(--ink);
    background: var(--surface); border: 1px solid var(--line); border-radius: 6px; padding: .3rem .5rem; }}
  .uc-f select:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 1px; }}
  .uc-out {{ margin: 0 0 .9rem; font-size: .87rem; color: var(--ink-2); }}
  .uc-out strong {{ color: var(--ink); font-weight: 600; }}
  .uc-out .uc-why {{ display: block; margin-top: .2rem; font-size: .78rem; color: var(--muted); }}
  .ix-row.uc-best {{ background: var(--ok-tint); box-shadow: inset 3px 0 0 0 var(--ok); }}
  .ix-row.uc-best:hover, .ix-row.uc-best:focus-visible {{ background: var(--ok-tint); }}
  .ix-row.uc-best .ix-name::after {{ content: "best here"; margin-left: .5rem;
    font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .58rem; letter-spacing: .08em;
    text-transform: uppercase; color: var(--ok); border: 1px solid var(--ok);
    border-radius: 3px; padding: .1em .3em; vertical-align: .1em; }}
  .ix-row.uc-out-of-scope {{ opacity: .5; }}
  .ix-head {{ font-size: .78rem; letter-spacing: .1em; text-transform: uppercase; color: var(--accent);
    margin: 0 0 .7rem; font-weight: 600; font-family: "IBM Plex Mono", ui-monospace, monospace; }}
  .ix-rows {{ display: flex; flex-direction: column; gap: 1px; background: var(--line);
    border: 1px solid var(--line); border-radius: 9px; overflow: hidden; }}
  .ix-row {{ display: grid; grid-template-columns: minmax(7rem, 1.5fr) 10.5rem minmax(5rem, .7fr) 5.5rem minmax(6rem, .95fr);
    align-items: center; gap: .9rem; padding: .62rem 1rem; background: var(--surface);
    text-decoration: none; color: inherit; border-left: 3px solid var(--medium);
    transition: background .12s ease; }}
  .ix-row:hover, .ix-row:focus-visible {{ background: var(--surface-2); }}
  .ix-row.v-ready {{ border-left-color: var(--ok); }}
  .ix-row.v-degraded {{ border-left-color: var(--warn); }}
  .ix-row.v-blocked {{ border-left-color: var(--critical); }}
  .ix-row.v-nofit, .ix-row.v-unknown {{ border-left-color: var(--low); }}
  .ix-name {{ font-weight: 600; font-size: .92rem; letter-spacing: -.01em; }}
  .ix-status {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .66rem;
    font-weight: 600; letter-spacing: .05em; text-transform: uppercase; white-space: nowrap;
    padding: .14rem .5rem; border-radius: 4px; border: 1px solid; justify-self: start; }}
  .ix-status.v-ready {{ color: var(--ok); border-color: var(--ok); }}
  .ix-status.v-degraded {{ color: var(--warn); border-color: var(--warn); }}
  .ix-status.v-blocked {{ color: var(--critical); border-color: var(--critical); }}
  .ix-status.v-nofit, .ix-status.v-unknown {{ color: var(--low); border-color: var(--line); }}
  .ix-size {{ text-align: right; font-variant-numeric: tabular-nums; font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .78rem;
    color: var(--ink-2); font-variant-numeric: tabular-nums; text-align: right; white-space: nowrap; }}
  .ix-meta {{ font-size: .76rem; color: var(--muted); text-align: right; white-space: nowrap; }}
  @media (max-width: 34rem) {{
    .ix-row {{ grid-template-columns: 1fr auto; row-gap: .3rem; }}
    .ix-size, .ix-meta {{ text-align: left; }}
    .ix-eng {{ order: 5; }}
  }}
  .model {{ margin-bottom: 2.5rem; scroll-margin-top: 5.75rem; }}
  .nofit-row {{ scroll-margin-top: 5.75rem; }}
  .model-head {{ background: var(--surface); border: 1px solid var(--line);
    border-top: 3px solid var(--medium); border-radius: 10px 10px 0 0; padding: 1.35rem 1.5rem 1.15rem; }}
  .model.v-degraded .model-head {{ border-top-color: var(--warn); }}
  .model.v-blocked .model-head {{ border-top-color: var(--critical); }}
  .model.v-unknown .model-head {{ border-top-color: var(--low); }}
  .model.v-ready .model-head {{ border-top-color: var(--ok); }}
  .model-id {{ display: flex; align-items: center; gap: .75rem; flex-wrap: wrap; margin-bottom: .9rem; }}
  .model-id h2 {{ font-size: 1.35rem; font-weight: 700; margin: 0; letter-spacing: -.02em; }}
  .verdict {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .7rem; font-weight: 600;
    letter-spacing: .06em; text-transform: uppercase; padding: .22rem .6rem; border-radius: 4px; border: 1px solid; }}
  .verdict.v-degraded {{ color: var(--warn); border-color: var(--warn); background: var(--surface-2); }}
  .verdict.v-blocked {{ color: var(--critical); border-color: var(--critical); background: var(--surface-2); }}
  .verdict.v-unknown {{ color: var(--low); border-color: var(--line); background: var(--surface-2); }}
  .verdict.v-ready {{ color: var(--ok); border-color: var(--ok); background: var(--surface-2); }}
  .vram {{ display: flex; align-items: baseline; gap: .7rem; flex-wrap: wrap;
    padding: .6rem .9rem; margin: 0 0 .7rem; border-radius: 6px;
    background: var(--surface-2); border: 1px solid var(--line-soft); border-left: 3px solid var(--accent); }}
  .vram.tight {{ border-left-color: var(--critical); }}
  .vram-k {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .66rem;
    letter-spacing: .1em; text-transform: uppercase; color: var(--muted); font-weight: 600; }}
  .vram-v {{ font-size: .87rem; font-weight: 600; color: var(--ink); font-variant-numeric: tabular-nums; }}
  .quants {{ display: flex; flex-direction: column; gap: .3rem; margin: 0 0 .9rem; }}
  .q-cat {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .64rem;
    letter-spacing: .1em; text-transform: uppercase; color: var(--muted); font-weight: 600; }}
  .q {{ display: flex; align-items: baseline; gap: .6rem; flex-wrap: wrap; font-size: .82rem; }}
  .q.alt {{ opacity: .72; }}
  .q-repo {{ font-family: "IBM Plex Mono", ui-monospace, monospace; color: var(--accent);
    text-decoration: none; border-bottom: 1px solid transparent; word-break: break-all; }}
  .q-repo:hover, .q-repo:focus-visible {{ border-bottom-color: var(--accent); }}
  .q-repo.none {{ color: var(--muted); font-style: italic; border: none; }}
  .q-size {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-weight: 600;
    color: var(--ink); font-variant-numeric: tabular-nums; white-space: nowrap; }}
  .q-note {{ font-size: .76rem; color: var(--muted); }}
  .srcs {{ display: flex; align-items: baseline; gap: .55rem; flex-wrap: wrap; margin: 0 0 .8rem; }}
  .src {{ font-size: .76rem; color: var(--accent); text-decoration: none;
    border: 1px solid var(--line); border-radius: 4px; padding: .1rem .45rem; background: var(--surface-2); }}
  .src:hover, .src:focus-visible {{ border-color: var(--accent); }}
  .nofit-row .srcs {{ margin-top: .4rem; margin-bottom: 0; }}
  .scores {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(15rem, 1fr)); gap: .9rem 1.6rem;
    margin: 0 0 1rem; padding: .85rem 1rem; background: var(--surface-2);
    border: 1px solid var(--line-soft); border-radius: 7px; }}
  .score-col {{ display: flex; flex-direction: column; gap: .32rem; min-width: 0; }}
  .score-cat {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .66rem;
    letter-spacing: .1em; text-transform: uppercase; color: var(--accent); font-weight: 600; margin-bottom: .1rem; }}
  .score {{ display: flex; justify-content: space-between; align-items: baseline; gap: .8rem;
    border-bottom: 1px dotted var(--line); padding-bottom: .2rem; }}
  .score-k {{ font-size: .8rem; color: var(--ink-2); }}
  .score-v {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .82rem;
    font-weight: 600; color: var(--ink); font-variant-numeric: tabular-nums; white-space: nowrap; }}
  .spec {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(11rem, 1fr));
    gap: .8rem 1.4rem; margin: 0 0 .95rem; }}
  .spec div {{ display: flex; flex-direction: column; gap: .1rem; min-width: 0; }}
  .spec dt {{ font-size: .68rem; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); font-weight: 600; }}
  .spec dd {{ margin: 0; font-size: .85rem; color: var(--ink); font-weight: 500; }}
  .model-note {{ margin: 0 0 .8rem; font-size: .91rem; color: var(--ink-2); max-width: 52rem; }}
  .blockers-label {{ margin: 0; font-family: "IBM Plex Mono", ui-monospace, monospace;
    font-size: .72rem; letter-spacing: .05em; text-transform: uppercase; color: var(--muted); }}
  .rows {{ list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 1px;
    background: var(--line); border: 1px solid var(--line); border-top: none; border-radius: 0 0 10px 10px; overflow: hidden; }}
  .row {{ background: var(--surface); border-left: 3px solid var(--medium); padding: .9rem 1.15rem; }}
  .row.sev-critical {{ border-left-color: var(--critical); }}
  .row.sev-high {{ border-left-color: var(--high); }}
  .row.sev-medium {{ border-left-color: var(--medium); }}
  .row.sev-low {{ border-left-color: var(--low); }}
  .row-head {{ display: flex; align-items: center; gap: .6rem; flex-wrap: wrap; margin-bottom: .3rem; }}
  .ref {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .8rem; font-weight: 500;
    color: var(--accent); text-decoration: none; border-bottom: 1px solid transparent; }}
  .ref:hover, .ref:focus-visible {{ border-bottom-color: var(--accent); }}
  .pill {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .66rem; font-weight: 600;
    letter-spacing: .05em; text-transform: uppercase; padding: .14rem .45rem; border-radius: 4px; border: 1px solid var(--line); }}
  .pill.open {{ color: var(--ink-2); background: var(--surface-2); }}
  .pill.merged {{ color: var(--ok); background: var(--surface-2); border-color: var(--ok); }}
  .pill.closed {{ color: var(--muted); background: var(--surface-2); }}
  .sev-tag {{ font-size: .71rem; color: var(--muted); margin-left: auto; letter-spacing: .04em; }}
  .row h4 {{ font-size: .93rem; font-weight: 600; margin: 0 0 .22rem; letter-spacing: -.005em; }}
  .row p {{ margin: 0; font-size: .86rem; color: var(--ink-2); max-width: 52rem; }}

  .model-fit {{ margin: 0; font-family: "IBM Plex Mono", ui-monospace, monospace;
    font-size: .8rem; color: var(--ink-2); }}
  .model-fit.toolarge {{ color: var(--critical); }}
  header {{ position: relative; }}
  .gh {{ position: absolute; top: 0; right: 0; display: inline-flex; align-items: center;
    gap: .4rem; text-decoration: none; color: var(--ink-2);
    border: 1px solid var(--line); border-radius: 999px; padding: .3rem .7rem .3rem .6rem;
    background: var(--surface); font-size: .78rem; font-weight: 500; }}
  .gh:hover {{ color: var(--ink); border-color: var(--accent); }}
  .gh svg {{ flex: none; }}
  @media (max-width: 620px) {{ header {{ padding-top: 2.2rem; }} }}
  .sub-stamp {{ color: var(--muted); white-space: nowrap; }}
  .ix-eng {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .72rem;
    color: var(--muted); white-space: nowrap; }}
  .panel-lead {{ margin: 0 0 1.15rem; font-size: .89rem; color: var(--ink-2); max-width: 54rem; }}
  .panel.wide {{ padding-bottom: 1.35rem; }}

  .eng {{ margin-top: 1px; }}
  .eng-tabs {{ display: flex; flex-wrap: wrap; gap: 1px; background: var(--line);
    border: 1px solid var(--line); border-bottom: none; }}
  .eng-tab {{ appearance: none; border: 0; cursor: pointer; text-align: left;
    background: var(--surface-2); color: var(--muted);
    padding: .6rem .85rem; display: flex; flex-direction: column; gap: .12rem;
    flex: 1 1 8.5rem; min-width: 7.5rem; font: inherit; border-top: 2px solid transparent; }}
  .eng-tab:hover {{ background: var(--surface); color: var(--ink-2); }}
  .eng-tab[aria-selected="true"] {{ background: var(--surface); color: var(--ink);
    border-top-color: var(--accent); }}
  .eng-tab-n {{ font-size: .84rem; font-weight: 600; letter-spacing: -.005em; }}
  .eng-tab-s {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .64rem;
    letter-spacing: .05em; text-transform: uppercase; color: var(--muted); }}
  .eng-tab[aria-selected="true"] .eng-tab-s.s-ready {{ color: var(--ok); }}
  .eng-tab[aria-selected="true"] .eng-tab-s.s-degraded {{ color: var(--warn); }}
  .eng-tab[aria-selected="true"] .eng-tab-s.s-blocked {{ color: var(--critical); }}
  .eng-tab .eng-tab-s.s-ready::before,
  .eng-tab .eng-tab-s.s-degraded::before,
  .eng-tab .eng-tab-s.s-blocked::before,
  .eng-tab .eng-tab-s.s-unknown::before {{
    content: ""; display: inline-block; width: .42rem; height: .42rem; border-radius: 50%;
    margin-right: .35rem; vertical-align: baseline; }}
  .eng-tab .eng-tab-s.s-ready::before {{ background: var(--ok); }}
  .eng-tab .eng-tab-s.s-degraded::before {{ background: var(--warn); }}
  .eng-tab .eng-tab-s.s-blocked::before {{ background: var(--critical); }}
  .eng-tab .eng-tab-s.s-unknown::before {{ background: var(--low); }}

  .eng-pane {{ background: var(--surface); border: 1px solid var(--line); border-top: none;
    padding: 1.15rem 1.2rem 1.2rem; display: flex; flex-direction: column; gap: .8rem; }}
  .model-fit {{ margin: 0 0 .35rem; }}
  .scores-wrap {{ margin-top: .9rem; border-top: 1px solid var(--line-soft); padding-top: .7rem; }}
  .scores-wrap > summary {{ cursor: pointer; font-family: "IBM Plex Mono", ui-monospace, monospace;
    font-size: .66rem; letter-spacing: .08em; text-transform: uppercase; color: var(--muted);
    font-weight: 600; list-style: none; display: flex; align-items: center; gap: .4rem; }}
  .scores-wrap > summary::-webkit-details-marker {{ display: none; }}
  .scores-wrap > summary::before {{ content: "+"; font-size: .85rem; line-height: 1;
    color: var(--accent); width: .7rem; }}
  .scores-wrap[open] > summary::before {{ content: "\\2212"; }}
  .scores-wrap > summary:hover {{ color: var(--ink-2); }}
  .scores-wrap .scores {{ margin-top: .6rem; }}
  .build-bpw {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .72rem;
    letter-spacing: .03em; padding: .1em .45em; border-radius: 4px; border: 1px solid var(--line); }}
  .build-bpw.b-full {{ color: var(--ok); border-color: var(--ok); }}
  .build-bpw.b-mild, .build-bpw.b-low, .build-bpw.b-pruned {{ color: var(--warn); border-color: var(--warn); }}
  .build-bpw.b-unusable {{ color: var(--critical); border-color: var(--critical); }}
  .fidelity {{ margin: 0; font-size: .85rem; color: var(--ink-2); padding: .65rem .8rem;
    border-left: 3px solid var(--warn); background: var(--surface-2); }}
  .fidelity.b-unusable {{ border-left-color: var(--critical); }}
  .fidelity strong {{ color: var(--ink); font-weight: 600; }}
  .fidelity.b-unusable strong {{ color: var(--critical); }}
  .ctx-wrap {{ display: flex; flex-direction: column; gap: .45rem; }}
  .ctx-k {{ font-size: .66rem; letter-spacing: .07em; text-transform: uppercase;
    color: var(--muted); font-weight: 600; }}
  .ctx {{ border-collapse: collapse; font-size: .82rem; width: 100%; max-width: 34rem; }}
  .ctx th {{ text-align: left; font-size: .64rem; letter-spacing: .06em; text-transform: uppercase;
    color: var(--muted); font-weight: 600; padding: .25rem .7rem .25rem 0;
    border-bottom: 1px solid var(--line); }}
  .ctx td {{ padding: .3rem .7rem .3rem 0; border-bottom: 1px solid var(--line-soft);
    font-variant-numeric: tabular-nums; color: var(--ink-2); }}
  .ctx th:last-child, .ctx td:last-child {{ text-align: right; padding-right: 0; }}
  .ctx-n {{ font-family: "IBM Plex Mono", ui-monospace, monospace; color: var(--ink); font-weight: 600; }}
  .ctx-n.none {{ color: var(--critical); font-weight: 400; }}
  .ctx-cap td {{ border-top: 1px solid var(--line); font-weight: 500; color: var(--ink); }}
  .ctx-cap .ctx-n {{ color: var(--ok); }}
  .ctx-why {{ margin: 0; font-size: .76rem; color: var(--muted); max-width: 46rem; }}

  .api {{ margin: 0; display: flex; flex-direction: column; gap: 1px;
    background: var(--line); border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }}
  .api-row {{ background: var(--surface-2); padding: .7rem .85rem; display: grid;
    grid-template-columns: 9.5rem 1fr; gap: .2rem 1rem; align-items: baseline; }}
  .api-row dt {{ font-size: .68rem; letter-spacing: .07em; text-transform: uppercase;
    color: var(--muted); font-weight: 600; }}
  .api-row dd {{ margin: 0; font-size: .85rem; color: var(--ink-2); }}
  .api-row:last-child dd {{ color: var(--ink-2); }}
  .api-row:last-child dt {{ color: var(--warn); }}
  .api-row code {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .8em;
    background: var(--surface); border: 1px solid var(--line-soft); border-radius: 4px;
    padding: .05em .3em; }}
  .api-row strong {{ color: var(--ink); font-weight: 600; }}
  @media (max-width: 640px) {{
    .api-row {{ grid-template-columns: 1fr; }}
  }}

  .eng-note code, .row p code, .model-note code {{ font-family: "IBM Plex Mono", ui-monospace, monospace;
    font-size: .82em; background: var(--surface-2); border: 1px solid var(--line-soft);
    border-radius: 4px; padding: .05em .3em; }}
  .eng-meta {{ margin: 0; display: grid; grid-template-columns: repeat(auto-fit, minmax(9rem, 1fr));
    gap: .55rem 1.2rem; }}
  .eng-meta div {{ display: flex; flex-direction: column; gap: .1rem; }}
  .eng-meta dt {{ font-size: .66rem; letter-spacing: .07em; text-transform: uppercase;
    color: var(--muted); font-weight: 500; }}
  .eng-meta dd {{ margin: 0; font-size: .82rem; color: var(--ink-2); }}
  .eng-fit {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .8rem;
    color: var(--ink-2); background: var(--surface-2); border-left: 3px solid var(--line);
    padding: .6rem .8rem; }}
  .eng-fit.s-ready {{ border-left-color: var(--ok); }}
  .eng-fit.s-degraded {{ border-left-color: var(--warn); }}
  .eng-fit.s-blocked {{ border-left-color: var(--critical); }}
  .eng-fit.toolarge {{ border-left-color: var(--critical); color: var(--critical); }}
  .eng-build {{ font-size: .8rem; display: flex; flex-wrap: wrap; gap: .5rem; align-items: baseline; }}
  .eng-build-k {{ font-size: .66rem; letter-spacing: .07em; text-transform: uppercase;
    color: var(--muted); font-weight: 500; }}
  .eng-build a, .eng-build span:not(.eng-build-k) {{
    font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .78rem; }}
  .eng-build.none span:not(.eng-build-k) {{ color: var(--muted); }}
  .eng-note {{ margin: 0; font-size: .89rem; color: var(--ink-2); max-width: 54rem; }}
  .eng-clear {{ margin: 0; font-size: .85rem; color: var(--muted); }}
  .eng-pane .rows, .eng-pane .cross-list {{ margin-top: .15rem; }}
  @media (max-width: 640px) {{
    .eng-tab {{ flex: 1 1 100%; }}
  }}
  .panel {{ background: var(--surface); border: 1px solid var(--line); border-radius: 10px;
    padding: 1.4rem 1.5rem; margin-bottom: 1rem; }}
  .panel h2 {{ font-size: .78rem; letter-spacing: .1em; text-transform: uppercase; color: var(--accent);
    margin: 0 0 1rem; font-weight: 600; font-family: "IBM Plex Mono", ui-monospace, monospace; }}
  .panel > ul {{ margin: 0; padding-left: 1.1rem; display: flex; flex-direction: column; gap: .55rem; }}
  .panel > ul > li {{ font-size: .89rem; color: var(--ink-2); }}
  .panel strong {{ color: var(--ink); font-weight: 600; }}
  .nofit {{ list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: .9rem; }}
  .nofit-row {{ border-left: 2px solid var(--line); padding-left: .9rem; }}
  .nofit-head {{ display: flex; align-items: baseline; gap: .7rem; flex-wrap: wrap; }}
  .nofit-head h4 {{ font-size: .95rem; font-weight: 600; margin: 0; }}
  .nofit-mem {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .8rem;
    color: var(--muted); font-variant-numeric: tabular-nums; }}
  .nofit-arch {{ margin: .12rem 0 .3rem; font-size: .78rem; color: var(--muted);
    font-family: "IBM Plex Mono", ui-monospace, monospace; }}
  .nofit-row > p:last-child {{ margin: 0; font-size: .86rem; color: var(--ink-2); }}
  .cross-list {{ list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 1px;
    background: var(--line); border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }}
  .rel {{ display: flex; justify-content: space-between; align-items: baseline; gap: 1rem;
    padding: .5rem 0; border-bottom: 1px solid var(--line-soft); }}
  .rel:last-child {{ border-bottom: none; }}
  .rel-repo {{ font-size: .87rem; color: var(--ink-2); display: flex; flex-direction: column; gap: .12rem; }}
  .rel-note {{ font-size: .74rem; color: var(--muted); }}
  .rel-tag {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .87rem;
    font-weight: 600; color: var(--ink); font-variant-numeric: tabular-nums; }}
  .disclaimer {{ margin: 2rem 0 0; padding: .95rem 1.15rem; border-radius: 8px;
    background: var(--surface-2); border: 1px solid var(--line);
    border-left: 3px solid var(--warn); font-size: .82rem; color: var(--ink-2); max-width: 54rem; }}
  .disclaimer strong {{ color: var(--ink); font-weight: 600; }}
  footer {{ margin-top: 1.25rem; padding-top: 1.2rem; border-top: 1px solid var(--line);
    font-size: .82rem; color: var(--muted); }}
  [hidden] {{ display: none !important; }}
  a {{ color: var(--accent); }}
  :focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; }}
</style>

<div class="wrap">
  <header>
    <a class="gh" href="https://github.com/dreamingwell/apple-llm-performance"
       target="_blank" rel="noopener" aria-label="Open source on GitHub">
      <svg viewBox="0 0 16 16" width="15" height="15" aria-hidden="true" focusable="false"><path fill="currentColor" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-2.98-.88-2.98-2.9 0-.83.3-1.51.79-2.04-.08-.2-.35-1 .08-2.07 0 0 .65-.2 2.13.79a7.2 7.2 0 0 1 1.94-.26c.66 0 1.32.09 1.94.26 1.48-1 2.13-.79 2.13-.79.43 1.07.16 1.87.08 2.07.49.53.79 1.21.79 2.04 0 2.03-1.21 2.7-2.99 2.9.31.27.58.79.58 1.6 0 1.15-.01 2.09-.01 2.38 0 .21.15.46.55.38A7.99 7.99 0 0 0 16 8c0-4.42-3.58-8-8-8Z"/></svg>
      <span>Open source</span>
    </a>
    <span class="eyebrow">Top Tier Open Weight Models on Apple Silicon</span>
    <h1>Apple LLM Performance Tracker</h1>
    <p class="sub">Select your Mac CPU model, RAM, and machine count below. Then view what AI models
    should run well on it &mdash; and those that won&rsquo;t.
    <span class="sub-stamp">Updated <time class="ago" datetime="{now_iso}">{now}</time>.</span></p>
  </header>

  <div id="rig-sentinel" aria-hidden="true"></div>
  <form class="rig" id="rig" aria-label="Cluster configuration">
    <div class="rig-controls">
      <label class="rig-f"><span>CPU Model</span>
        <select id="rig-chip"></select>
      </label>
      <label class="rig-f"><span>Memory each</span>
        <select id="rig-mem"></select>
      </label>
      <label class="rig-f"><span>Units</span>
        <select id="rig-n"></select>
      </label>
    </div>
    <p class="rig-out" id="rig-out"></p>
    <p class="rig-warn" id="rig-warn" hidden></p>
  </form>

  <nav class="index" aria-label="Model index">
    <div class="ix-top">
      <h2 class="ix-head">Models at a glance</h2>
      <label class="uc-f"><span>What for?</span>
        <select id="uc-sel"></select>
      </label>
    </div>
    <p class="uc-out" id="uc-out"></p>
    <div class="ix-rows">{index}
    </div>
  </nav>
{cards}

  <div class="panel wide">
    <h2>General engine information</h2>
    <p class="panel-lead">What each engine is, what its API actually implements, and the defects that follow
    you whichever model you load on it. All seven speak OpenAI on <code>/v1/chat/completions</code> with SSE
    streaming, and none is desktop-only &mdash; but &ldquo;OpenAI-compatible&rdquo; covers a wide range, and the
    differences land on exactly the features an agent leans on: whether tool-call arguments stream as deltas or
    arrive only after the turn, whether constrained decoding exists at all, and whether <code>tool_choice</code>
    is implemented. Five of the seven also serve Anthropic <code>/v1/messages</code>, so Claude Code can point
    at them directly.</p>
    {cross}
  </div>

  <div class="panel">
    <h2>Reading the scores</h2>
    <ul>
      <li><strong>Terminal-Bench 2.0 and 2.1 are different benchmarks.</strong> GLM-4.7's 41.0 and Qwen3-Coder-Next's 36.2 are on v2.0; Qwen3.8-27B's 73.0 and GLM-5.2's 81.0 are on v2.1. Do not rank across the two &mdash; they are shown labelled, not normalised.</li>
      <li>Scores are vendor-reported or aggregator-reported, not reproduced here. Treat them as a shortlist filter, then verify the shortlist on your own context-rot harness.</li>
      <li>Nothing on this page has been measured on M5 Ultra hardware. Everything else is published numbers.</li>
      <li>Weights are the summed file sizes of the linked repository &mdash; safetensors for MLX builds, GGUF for the rest &mdash; measured, not estimated. A <strong>*</strong> marks the exception: a figure derived from parameter count because no build has been published anywhere.</li>
      <li><strong>The same model weighs different amounts on different engines.</strong> GGUF has quant tiers MLX does not, so llama.cpp can often fit a model MLX cannot &mdash; GLM-4.7 is 158.7 GB at UD-Q3_K_XL against 198.6 GB for the MLX 4-bit. Each engine tab states its own build and its own fit.</li>
      <li>Issue lists are scoped to the engine tab you are on, and are filtered for what actually applies on a Mac. A CUDA-only or ROCm-only report is not listed here even when it dominates the upstream thread.</li>
      <li>Fit assumes a 90% wired-memory limit plus ~10 GB of framework overhead, and that pooling shards weights evenly. It answers "does this load", not "does this run well" &mdash; a model spread across machines still pays the Thunderbolt hop on every token.</li>
    </ul>
  </div>

  <p class="disclaimer">
    <strong>Disclaimer.</strong> All of this is best effort and provided for entertainment purposes only.
    No warranty is given as to its accuracy. Benchmark scores are vendor- or aggregator-reported and are not
    reproduced here; issue states are a twice-daily snapshot; hardware figures are arithmetic, not measurements.
    Verify anything you intend to spend money on.
  </p>

  <footer>
    Polled twice daily against the GitHub API across llama.cpp, Ollama, LM Studio, oMLX, vllm-mlx, mlx-lm and ds4;
    state changes only &mdash; open&rarr;closed, merged, new release tag. The clock in the intro counts from the
    last <em>content</em> change, not the last check &mdash; the page is only republished when something actually
    moves, so a large number there means the watchlist has been quiet.
  </footer>
</div>

<script data-newblock="1">
(function () {{
  // Every M-series chip, its peak memory bandwidth, and the union of unified-memory
  // options across every Mac that shipped with it - laptops, mini, iMac, Studio and
  // Mac Pro - because the chip is what decides whether a model fits, not the case.
  // tb5 marks Thunderbolt 5, which is what RDMA and JACCL tensor parallelism need;
  // everything older pools only over the ring/pipeline path.
  // gen groups the dropdown. bwNote flags chips with a binned lower-bandwidth variant.
  var MACHINES = {{
    m1:       {{ label: "M1",       gen: "M1", bw: 68,   mem: [8, 16],                tb: "Thunderbolt 3 / USB4", link: 40, tb5: false, ports: 2 }},
    m1pro:    {{ label: "M1 Pro",   gen: "M1", bw: 200,  mem: [16, 32],               tb: "Thunderbolt 4", link: 40, tb5: false, ports: 3 }},
    m1max:    {{ label: "M1 Max",   gen: "M1", bw: 400,  mem: [32, 64],               tb: "Thunderbolt 4", link: 40, tb5: false, ports: 4 }},
    m1ultra:  {{ label: "M1 Ultra", gen: "M1", bw: 800,  mem: [64, 128],              tb: "Thunderbolt 4", link: 40, tb5: false, ports: 6 }},
    m2:       {{ label: "M2",       gen: "M2", bw: 100,  mem: [8, 16, 24],            tb: "Thunderbolt 4", link: 40, tb5: false, ports: 2 }},
    m2pro:    {{ label: "M2 Pro",   gen: "M2", bw: 200,  mem: [16, 32],               tb: "Thunderbolt 4", link: 40, tb5: false, ports: 4 }},
    m2max:    {{ label: "M2 Max",   gen: "M2", bw: 400,  mem: [32, 64, 96],           tb: "Thunderbolt 4", link: 40, tb5: false, ports: 4 }},
    m2ultra:  {{ label: "M2 Ultra", gen: "M2", bw: 800,  mem: [64, 128, 192],         tb: "Thunderbolt 4", link: 40, tb5: false, ports: 6 }},
    m3:       {{ label: "M3",       gen: "M3", bw: 100,  mem: [8, 16, 24],            tb: "Thunderbolt 4", link: 40, tb5: false, ports: 2 }},
    m3pro:    {{ label: "M3 Pro",   gen: "M3", bw: 150,  mem: [18, 36],               tb: "Thunderbolt 4", link: 40, tb5: false, ports: 3 }},
    m3max:    {{ label: "M3 Max",   gen: "M3", bw: 400,  mem: [36, 48, 64, 96, 128],  tb: "Thunderbolt 4", link: 40, tb5: false, ports: 3,
                bwNote: "300 GB/s on the binned 14-core CPU / 30-core GPU part" }},
    m3ultra:  {{ label: "M3 Ultra", gen: "M3", bw: 819,  mem: [96, 256, 512],         tb: "Thunderbolt 5", link: 80, tb5: true,  ports: 6 }},
    m4:       {{ label: "M4",       gen: "M4", bw: 120,  mem: [16, 24, 32],           tb: "Thunderbolt 4", link: 40, tb5: false, ports: 2 }},
    m4pro:    {{ label: "M4 Pro",   gen: "M4", bw: 273,  mem: [24, 48, 64],           tb: "Thunderbolt 5", link: 80, tb5: true,  ports: 3 }},
    m4max:    {{ label: "M4 Max",   gen: "M4", bw: 546,  mem: [36, 48, 64, 128],      tb: "Thunderbolt 5", link: 80, tb5: true,  ports: 4,
                bwNote: "410 GB/s on the binned 14-core CPU part" }},
    m5:       {{ label: "M5",       gen: "M5", bw: 153,  mem: [16, 24, 32],           tb: "Thunderbolt 4", link: 40, tb5: false, ports: 2 }},
    m5pro:    {{ label: "M5 Pro",   gen: "M5", bw: 307,  mem: [24, 48, 64],           tb: "Thunderbolt 5", link: 80, tb5: true,  ports: 3 }},
    m5max:    {{ label: "M5 Max",   gen: "M5", bw: 614,  mem: [36, 48, 64, 128],      tb: "Thunderbolt 5", link: 80, tb5: true,  ports: 4,
                bwNote: "460 GB/s on the 32-core GPU part; 614 on the 40-core" }},
    m5ultra:  {{ label: "M5 Ultra", gen: "M5", bw: 1200, mem: [96, 256, 512],         tb: "Thunderbolt 5", link: 80, tb5: true,  ports: 6 }}
  }};
  var GENS = ["M5", "M4", "M3", "M2", "M1"];
  var USE_CASES = {usecases};
  var BAND_RANK = {{ full: 0, mild: 1, low: 2, pruned: 2, unusable: 3 }};
  var ORDER = Object.keys(MACHINES);
  var MAX_UNITS = 6, PRACTICAL_UNITS = 4, OVERHEAD = 10, WIRED = 0.90;
  var BANDS = {bands};


  var chipSel = document.getElementById("rig-chip"),
      memSel  = document.getElementById("rig-mem"),
      nSel    = document.getElementById("rig-n"),
      out     = document.getElementById("rig-out"),
      warn    = document.getElementById("rig-warn");
  if (!chipSel) return;

  var DEF_CHIP = "m5ultra", DEF_MEM = 256, DEF_N = 1;

  var q = new URLSearchParams(location.search);
  var chip = MACHINES[q.get("chip")] ? q.get("chip") : DEF_CHIP;
  var mem  = parseInt(q.get("mem"), 10);
  if (!mem || MACHINES[chip].mem.indexOf(mem) === -1) {{
    mem = MACHINES[chip].mem.indexOf(DEF_MEM) !== -1 ? DEF_MEM : MACHINES[chip].mem[0];
  }}
  var n = parseInt(q.get("n"), 10);
  if (!n || n < 1 || n > MAX_UNITS) n = DEF_N;

  GENS.forEach(function (g) {{
    var grp = document.createElement("optgroup");
    grp.label = g;
    ORDER.filter(function (k) {{ return MACHINES[k].gen === g; }}).forEach(function (k) {{
      var o = document.createElement("option");
      o.value = k; o.textContent = MACHINES[k].label;
      grp.appendChild(o);
    }});
    chipSel.appendChild(grp);
  }});
  for (var i = 1; i <= MAX_UNITS; i++) {{
    var o = document.createElement("option");
    o.value = i; o.textContent = i + (i === 1 ? " machine" : " machines");
    nSel.appendChild(o);
  }}

  function fillMem(keepIfPossible) {{
    var opts = MACHINES[chip].mem;
    memSel.innerHTML = "";
    opts.forEach(function (g) {{
      var o = document.createElement("option");
      o.value = g; o.textContent = g + " GB";
      memSel.appendChild(o);
    }});
    if (opts.indexOf(keepIfPossible) === -1) {{
      keepIfPossible = opts.indexOf(DEF_MEM) !== -1 ? DEF_MEM : opts[opts.length - 1];
    }}
    memSel.value = keepIfPossible;
  }}

  function fmt(gb) {{ return gb >= 1000 ? (gb / 1000).toFixed(2) + " TB" : Math.round(gb) + " GB"; }}

  function apply() {{
    chip = chipSel.value;
    var g = parseInt(memSel.value, 10);
    n = parseInt(nSel.value, 10);
    var perNode = g * WIRED, cluster = perNode * n, M = MACHINES[chip];

    // The interconnect only matters once there is something to interconnect.
    out.innerHTML = "<strong>" + n + " \u00d7 " + M.label + " " + g + " GB</strong> = " +
      fmt(g * n) + " pooled, about " + fmt(cluster) + " usable after the wired-memory limit. " +
      "Per-machine bandwidth " + (M.bw >= 1000 ? (M.bw / 1000).toFixed(1) + " TB/s" : M.bw + " GB/s") + "." +
      (n > 1 ? " Uses " + M.tb + " with " + M.link + " Gb/s connection speed." : "");

    if (n > 1 && !M.tb5) {{
      warn.hidden = false;
      warn.textContent = "Clustering multiple " + M.label + " machines will be very slow: " + M.tb +
        " has no RDMA path, so pooling falls back to ring pipeline parallelism.";
    }} else if (n > PRACTICAL_UNITS) {{
      warn.hidden = false;
      warn.textContent = "Past " + PRACTICAL_UNITS + " machines a full Thunderbolt mesh runs out of ports. " +
        "Treat these rows as arithmetic, not a supported setup.";
    }} else {{ warn.hidden = true; }}

    function fitDetail(w) {{
      var resident = w + OVERHEAD;
      var nodes = Math.ceil(resident / perNode);
      if (resident > cluster) {{
        return {{ tooBig: true, nodes: nodes, resident: resident, free: 0,
                 short: "needs " + nodes + " machine" + (nodes === 1 ? "" : "s"),
                 text: "needs " + nodes + " machine" + (nodes === 1 ? "" : "s") }};
      }}
      if (nodes > 1) {{
        var freeP = cluster - resident;
        return {{ tooBig: false, nodes: nodes, resident: resident, free: freeP, copies: 1,
                 short: fmt(freeP) + " free",
                 text: "pooled across " + nodes + " of your " + n + ", " + fmt(freeP) + " left for KV" }};
      }}
      // It fits on one machine, so every machine runs its own copy. Nothing is
      // pooled and nothing is shared - the capacity simply multiplies.
      var free = perNode - resident;
      return {{ tooBig: false, nodes: 1, resident: resident, free: free, copies: n,
               short: fmt(free) + " free",
               text: n > 1
                 ? fmt(free) + " free for KV per machine \u2014 run as individual compute, not as a cluster"
                 : fmt(free) + " free for KV" }};
    }}

    // Pick the target build for this cluster - not simply the biggest thing that
    // fits. Measured KL divergence flattens above 4 bits per weight (0.41 at
    // Q4_K_XL against 0.24 at Q5 and 0.10 at Q8), so paying an extra 200 GB for
    // Q8 buys almost nothing and costs the KV headroom that decides how much
    // context and how many concurrent streams you get. So: the CHEAPEST rung
    // that still clears 4 bits, and only if none does, the best of what is left.
    function pick(ladder) {{
      var fits = ladder.filter(function (r) {{ return r.gb + OVERHEAD <= cluster; }});
      if (!fits.length) return null;
      var full = fits.filter(function (r) {{ return r.kind !== "pruned" && r.bpw >= 4; }});
      if (full.length) return full[full.length - 1];   // ladder is largest-first
      return fits[0];                                  // best available below 4 bpw
    }}

    function band(rung) {{
      if (rung.kind === "pruned") {{
        return {{ k: "pruned", label: "Expert-pruned",
                 why: "This build was not quantised down, it was pruned: whole experts were scored and " +
                      "deleted. The surviving weights are near lossless, and the capacity they came from " +
                      "is gone. Bits per weight does not describe this loss." }};
      }}
      for (var i = 0; i < BANDS.length; i++) {{
        if (rung.bpw >= BANDS[i][0]) {{
          return {{ k: BANDS[i][1], label: BANDS[i][2], why: BANDS[i][3] }};
        }}
      }}
      return {{ k: "unusable", label: "Below agentic-usable", why: "" }};
    }}

    // freeGB is per machine when the model fits on one, so multiply the stream
    // count by the number of copies to get the total the whole group serves.
    function ctxRows(bpt, maxctx, freeGB, copies) {{
      if (!bpt || !maxctx || freeGB <= 0) return [];
      copies = copies || 1;
      var out = [];
      [[1, "full"], [0.75, "three quarters"], [0.5, "half"], [0.25, "a quarter"]].forEach(function (f) {{
        var tok = Math.round(maxctx * f[0]);
        var per = bpt * tok;                       // bytes
        out.push({{ tok: tok, frac: f[1], perGB: per / 1e9,
                   streams: Math.floor((freeGB * 1e9) / per) * copies }});
      }});
      // A model can load and still have no room for a quarter of its advertised
      // window - MiniMax M3 on one 256 GB machine is exactly that. Saying "runs"
      // above four rows of "does not fit" is useless, so state what does fit.
      if (out[out.length - 1].streams < 1) {{
        var maxTok = Math.floor((freeGB * 1e9) / bpt);
        out.push({{ tok: maxTok, frac: "largest that fits", cap: true,
                   perGB: (bpt * maxTok) / 1e9, streams: maxTok >= 2048 ? copies : 0 }});
      }}
      return out;
    }}

    function tokFmt(t) {{
      return t >= 1000000 ? (t / 1000000).toFixed(t % 1000000 ? 2 : 0) + "M"
                          : Math.round(t / 1000) + "k";
    }}

    document.querySelectorAll("[data-payload]").forEach(function (el) {{
      var pl;
      try {{ pl = JSON.parse(el.getAttribute("data-payload")); }} catch (e) {{ return; }}
      var engs = pl.engines || [];

      var chosen = null, rung = null;
      for (var i = 0; i < engs.length; i++) {{
        var r = pick(engs[i].ladder);
        if (r) {{ chosen = engs[i]; rung = r; break; }}
      }}
      if (!chosen && engs.length) {{
        // nothing fits anywhere: report whichever engine has the smallest build
        chosen = engs.reduce(function (a, b) {{
          return b.ladder[b.ladder.length - 1].gb < a.ladder[a.ladder.length - 1].gb ? b : a;
        }});
        rung = chosen.ladder[chosen.ladder.length - 1];
      }}
      if (!chosen) {{
        var f0 = el.querySelector(".fit");
        if (f0) f0.textContent = "no build published";
        return;
      }}

      var f = fitDetail(rung.gb);
      var bd = band(rung);
      var cls, label;
      if (chosen.s === "blocked" || chosen.s === "unknown") {{
        cls = chosen.s; label = chosen.label;
      }} else if (f.tooBig) {{
        cls = "toolarge"; label = "Too large";
      }} else if (bd.k === "unusable") {{
        cls = "blocked"; label = "Too degraded";
      }} else if (bd.k === "mild" || bd.k === "low" || bd.k === "pruned") {{
        cls = "degraded"; label = chosen.s === "ready" ? "Runs, " + bd.label.toLowerCase() : chosen.label;
      }} else {{
        cls = chosen.s; label = chosen.label;
      }}

      if (el.classList.contains("ix-row")) {{
        el.__pick = {{ model: el.querySelector(".ix-name").textContent.trim(), engine: chosen.name,
                      engineId: chosen.id, gb: rung.gb, bpw: rung.bpw, band: bd.k,
                      tooBig: f.tooBig || bd.k === "unusable" || chosen.s === "blocked" }};
        el.className = "ix-row v-" + cls;
        var st = el.querySelector(".ix-status");
        st.className = "ix-status v-" + cls;
        st.textContent = label;
        el.querySelector(".ix-eng").textContent = chosen.name;
        el.querySelector(".ix-size").textContent = fmt(rung.gb);
        el.querySelector(".fit").textContent = f.short;
        return;
      }}

      el.className = "model v-" + cls;
      // Open the card on the engine the glance row names for this cluster, so the
      // two never disagree - unless the reader has already picked a tab by hand.
      var grp = el.querySelector(".eng");
      if (grp && !grp.hasAttribute("data-user-picked")) {{
        var want = grp.querySelector('.eng-tab[data-eng="' + chosen.id + '"]');
        if (want && want.getAttribute("aria-selected") !== "true") {{
          grp.querySelectorAll(".eng-tab").forEach(function (t) {{
            t.setAttribute("aria-selected", t === want ? "true" : "false");
          }});
          grp.querySelectorAll(".eng-pane").forEach(function (pa) {{
            pa.hidden = pa.getAttribute("data-eng") !== chosen.id;
          }});
        }}
      }}
      var vb = el.querySelector(".verdict");
      vb.className = "verdict v-" + cls;
      vb.textContent = label;
      var mf = el.querySelector(".model-fit");
      if (mf) {{
        mf.className = "model-fit" + (f.tooBig ? " toolarge" : "");
        mf.textContent = chosen.s === "blocked"
          ? "No engine here can load this yet \u2014 see the tabs below for why."
          : f.tooBig
            ? "Does not fit. Smallest build is " + chosen.name + " at " + fmt(rung.gb) + ", which " + f.text + "."
            : "Best fit here: " + chosen.name + ", " + fmt(rung.gb) + " resident, " + f.text + ".";
      }}

      // Each engine tab reports its own rung on the same cluster.
      engs.forEach(function (eng) {{
        var pane = el.querySelector('.eng-pane[data-eng="' + eng.id + '"]');
        if (!pane) return;
        var fit = pane.querySelector(".eng-fit");
        if (!fit || !fit.hasAttribute("data-has-ladder")) return;
        var r = pick(eng.ladder) || eng.ladder[eng.ladder.length - 1];
        var pf = fitDetail(r.gb), pb = band(r);

        fit.classList.toggle("toolarge", pf.tooBig);
        fit.textContent = pf.tooBig
          ? "Too large: " + fmt(pf.resident) + " resident, " + pf.text + "."
          : fmt(pf.resident) + " resident on this cluster, " + pf.text + ".";

        var link = pane.querySelector(".build-link"), bpw = pane.querySelector(".build-bpw");
        if (link) {{
          link.textContent = r.label;
          link.setAttribute("href", "https://huggingface.co/" + r.repo);
        }}
        if (bpw) {{
          bpw.textContent = r.kind === "pruned" ? "expert-pruned" : r.bpw.toFixed(2) + " bits/weight";
          bpw.className = "build-bpw b-" + pb.k;
        }}

        var fid = pane.querySelector(".fidelity");
        if (fid) {{
          if (pb.k === "full") {{
            fid.hidden = true;
          }} else {{
            fid.hidden = false;
            fid.className = "fidelity b-" + pb.k;
            fid.innerHTML = "<strong>" + pb.label + ".</strong> " + pb.why +
              (eng.note ? " " + eng.note : "");
          }}
        }}

        var wrap = pane.querySelector(".ctx-wrap");
        if (wrap) {{
          var rows = pf.tooBig ? [] : ctxRows(pl.kv.bpt, pl.kv.maxctx, pf.free, pf.copies);
          if (!rows.length) {{
            wrap.hidden = true;
          }} else {{
            wrap.hidden = false;
            wrap.querySelector("tbody").innerHTML = rows.map(function (c) {{
              var label = c.cap ? tokFmt(c.tok) + " &mdash; " + c.frac
                                : tokFmt(c.tok) + " (" + c.frac + ")";
              return "<tr" + (c.cap ? ' class="ctx-cap"' : "") + "><td>" + label + "</td><td>" +
                     (c.perGB < 1 ? (c.perGB * 1000).toFixed(0) + " MB" : c.perGB.toFixed(1) + " GB") +
                     '</td><td class="ctx-n' + (c.streams < 1 ? ' none' : '') + '">' +
                     (c.streams < 1 ? "does not fit" : c.streams) + "</td></tr>";
            }}).join("");
            wrap.querySelector(".ctx-why").textContent =
              "KV at fp16: " + (pl.kv.bpt / 1024).toFixed(1) + " KiB per token. " + pl.kv.why + ". " +
              (pf.copies > 1 ? "Stream counts are the total across all " + pf.copies +
                               " machines, each running its own copy. " : "") +
              "Quantising the KV cache to 8-bit doubles every count above.";
          }}
        }}
      }});
    }});

    // The winner for the selected job: walk the curated ranking and take the
    // first model that both fits and clears that job's fidelity gate. Ranking is
    // fixed at build time because the benchmarks are not mutually comparable;
    // what changes with the cluster is only which entries are reachable.
    var ucId = ucSel ? ucSel.value : "";
    var uc = null;
    for (var ui = 0; ui < USE_CASES.length; ui++) {{
      if (USE_CASES[ui].id === ucId) {{ uc = USE_CASES[ui]; break; }}
    }}
    document.querySelectorAll(".ix-row").forEach(function (r) {{
      r.classList.remove("uc-best", "uc-out-of-scope");
    }});
    if (!uc) {{
      if (ucOut) ucOut.innerHTML = "";
      document.querySelectorAll(".ix-row").forEach(function (r) {{ r.style.order = ""; }});
    }} else {{
      var inScope = {{}};
      uc.rank.forEach(function (r) {{ inScope[r[0]] = true; }});
      var winner = null;
      for (var ri = 0; ri < uc.rank.length; ri++) {{
        var row = document.querySelector('.ix-row[data-model="' + uc.rank[ri][0] + '"]');
        if (!row || !row.__pick || row.__pick.tooBig) continue;
        if (BAND_RANK[row.__pick.band] > BAND_RANK[uc.gate]) continue;
        winner = {{ row: row, entry: uc.rank[ri] }};
        break;
      }}
      // Rank order for the chosen job, then everything that does not fit or does
      // not publish a number for it. The container is a flex column, so `order`
      // re-sequences without touching the DOM.
      var pos = {{}};
      uc.rank.forEach(function (r, i) {{ pos[r[0]] = i; }});
      document.querySelectorAll(".ix-row").forEach(function (r) {{
        var mid = r.getAttribute("data-model");
        var ranked = pos[mid] !== undefined;
        if (!ranked) r.classList.add("uc-out-of-scope");
        var usable = ranked && r.__pick && !r.__pick.tooBig &&
                     BAND_RANK[r.__pick.band] <= BAND_RANK[uc.gate];
        // three tiers: usable in rank order, then ranked-but-unusable, then unranked
        r.style.order = usable ? pos[mid] : (ranked ? 200 + pos[mid] : 400);
      }});
      if (winner) {{
        winner.row.classList.add("uc-best");
        var pk = winner.row.__pick;
        ucOut.innerHTML = "Best for <strong>" + uc.label.toLowerCase() + "</strong> on this cluster: " +
          "<strong>" + pk.model + "</strong> via " + pk.engine + ", " + fmt(pk.gb) + " at " +
          (pk.band === "pruned" ? "expert-pruned precision" : pk.bpw.toFixed(2) + " bits/weight") +
          " &mdash; " + winner.entry[1] + " " + winner.entry[2] + "." +
          "<span class='uc-why'>" + uc.axis + " Dimmed rows publish no number for this job.</span>";
      }} else {{
        ucOut.innerHTML = "<strong>Nothing suitable fits this cluster.</strong>" +
          "<span class='uc-why'>Every model ranked for " + uc.label.toLowerCase() +
          " is either too large here, or only fits at a precision below what this job tolerates. " +
          "Add memory, add a machine, or pick a different job.</span>";
      }}
    }}

    var p = new URLSearchParams();
    p.set("chip", chip); p.set("mem", g); p.set("n", n);
    if (ucId) p.set("uc", ucId);
    history.replaceState(null, "", location.pathname + "?" + p.toString());
  }}

  var ucSel = document.getElementById("uc-sel"), ucOut = document.getElementById("uc-out");
  if (ucSel) {{
    var o0 = document.createElement("option");
    o0.value = ""; o0.textContent = "Anything - just show me the list";
    ucSel.appendChild(o0);
    USE_CASES.forEach(function (u) {{
      var o = document.createElement("option");
      o.value = u.id; o.textContent = u.label;
      ucSel.appendChild(o);
    }});
    var uc0 = q.get("uc");
    if (uc0 && USE_CASES.some(function (u) {{ return u.id === uc0; }})) ucSel.value = uc0;
    ucSel.addEventListener("change", apply);
  }}

  var sentinel = document.getElementById("rig-sentinel");
  var rigEl = document.getElementById("rig");
  if (sentinel && rigEl && "IntersectionObserver" in window) {{
    new IntersectionObserver(function (entries) {{
      rigEl.classList.toggle("stuck", !entries[0].isIntersecting);
    }}, {{ threshold: 1 }}).observe(sentinel);
  }}

  chipSel.value = chip;
  fillMem(mem);
  nSel.value = n;
  chipSel.addEventListener("change", function () {{ chip = chipSel.value; fillMem(parseInt(memSel.value, 10)); apply(); }});
  memSel.addEventListener("change", apply);
  nSel.addEventListener("change", apply);
  apply();
}})();
</script>

<script>
  (function () {{
    document.querySelectorAll(".eng").forEach(function (grp) {{
      var tabs = [].slice.call(grp.querySelectorAll(".eng-tab"));
      var panes = [].slice.call(grp.querySelectorAll(".eng-pane"));
      function show(t) {{
        tabs.forEach(function (x) {{ x.setAttribute("aria-selected", x === t ? "true" : "false"); }});
        var id = t.getAttribute("data-eng");
        panes.forEach(function (p) {{ p.hidden = p.getAttribute("data-eng") !== id; }});
      }}
      tabs.forEach(function (t, i) {{
        t.addEventListener("click", function () {{ grp.setAttribute("data-user-picked", "1"); show(t); }});
        t.addEventListener("keydown", function (ev) {{
          var d = ev.key === "ArrowRight" ? 1 : ev.key === "ArrowLeft" ? -1 : 0;
          if (!d) return;
          ev.preventDefault();
          var next = tabs[(i + d + tabs.length) % tabs.length];
          show(next);
          next.focus();
        }});
      }});
    }});
  }})();
</script>

<script>
  (function () {{
    var el = document.querySelector("time.ago");

    if (!el) return;
    var t = Date.parse(el.getAttribute("datetime"));
    if (isNaN(t)) return;
    var abs = el.textContent;
    function render() {{
      var mins = Math.floor((Date.now() - t) / 60000);
      if (mins < 0) mins = 0;
      var out;
      if (mins < 1) out = "just now";
      else if (mins < 60) out = mins + "m ago";
      else if (mins < 1440) out = Math.floor(mins / 60) + "h " + (mins % 60) + "m ago";
      else out = Math.floor(mins / 1440) + "d " + Math.floor((mins % 1440) / 60) + "h ago";
      el.textContent = out;
      el.title = abs;
    }}
    render();
    setInterval(render, 60000);
  }})();
</script>
"""

if __name__ == "__main__":  # pragma: no cover - use tracker/build.py instead
    raise SystemExit("run: python3 tracker/build.py")
