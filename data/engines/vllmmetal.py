"""vLLM Metal - engine record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'vllmmetal'
NAME = 'vLLM Metal'
# Tab position on every card. Explicit so adding an engine cannot silently
# reshuffle the others; leave gaps of 10 to make insertion cheap.
DISPLAY_ORDER = 50
MODALITIES = ['text']
FORMAT = 'MLX'
INTERFACE = 'CLI + the standard vLLM server'
API = 'OpenAI, via vLLM core'
LICENSE = 'Apache-2.0'
REPO = 'vllm-project/vllm-metal'

RELEASE_FEED = {'repo': 'vllm-project/vllm-metal', 'scheme': 'release', 'note': ''}

WHAT = ('vLLM itself, running on Apple Silicon. This is a plugin in the vllm-project org that keeps '
 'vLLM core and swaps the compute layer for MLX, unifying MLX and PyTorch under one lowering '
 "path - so you get vLLM's scheduler, paged KV, continuous batching and API surface rather "
 'than a lookalike. Despite the name it is an MLX engine underneath: it pins a single exact '
 'MLX version, pulls in mlx-lm and mlx-vlm, and builds its Metal kernels as MLX primitives. '
 "Two things make it worth attention on new hardware: v0.2.0's unified paged varlen Metal "
 'kernel claims 83x TTFT and 3.6x throughput over v0.1.0, and as of August 2026 it uses the '
 '**M5 Neural Accelerator tensor units** to speed up MHA, GQA and MQA prefill - the only '
 'engine here that claims M5-specific acceleration. The cost is coverage: its model matrix is '
 'a curated list, not everything that exists.')

API_DETAIL = {'endpoints': 'Whatever vLLM core exposes, because this is vLLM: /v1/chat/completions, '
              '/v1/completions, /v1/embeddings, /v1/models, plus the pooling and rerank routes '
              'for the embedding and reranker models it supports.',
 'streaming': "vLLM's own implementation rather than a reimplementation, so streaming, usage "
              'accounting and the rest behave the way the upstream docs say they do.',
 'tools': "vLLM's tool parsers and guided decoding, again inherited from core. One live defect "
          'to know about: mixed batches with top_k enabled on some requests and disabled on '
          'others crash the Metal sampler.',
 'structured': "vLLM's guided decoding stack.",
 'concurrency': 'Continuous batching and paged KV from vLLM core, over Metal kernels. '
                'Automatic prefix caching is on by default for unified paged-KV models; hybrid '
                'GDN models like Qwen3.8 must opt in with --enable-prefix-caching.',
 'gotcha': "Model coverage is far narrower than llama.cpp's - this is a young plugin with a "
           'deliberately curated matrix, not a general loader. Check the supported-models '
           'table before planning around it. Needs macOS 15+ and native arm64 Python 3.12 '
           'specifically. And note the MLX pin is exact, not a floor: the prebuilt kernels '
           'link MLX private headers and libmlx.dylib carries no SONAME version, so a wheel is '
           'only ABI-safe against the one MLX it was built against. You cannot upgrade MLX '
           'underneath it.'}

# Issues that affect every model on this engine.
CROSS_ISSUES = ['vllm-project/vllm-metal#646',
 'vllm-project/vllm-metal#482',
 'vllm-project/vllm-metal#450',
 'vllm-project/vllm-metal#360']

# Quant family this engine loads.
QUANT_FAMILY = 'mlx'
