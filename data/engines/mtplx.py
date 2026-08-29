"""MTPLX - engine record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'mtplx'
NAME = 'MTPLX'
# Tab position on every card. Explicit so adding an engine cannot silently
# reshuffle the others; leave gaps of 10 to make insertion cheap.
DISPLAY_ORDER = 85
MODALITIES = ['text']
FORMAT = 'MLX + MTP head'
INTERFACE = 'Mac app + CLI + server'
API = 'OpenAI and Anthropic'
LICENSE = 'Apache-2.0'
REPO = 'youssofal/MTPLX'

# Canonical website, linked wherever this engine is named in prose.
SITE = 'https://mtplx.com'

# The names this engine actually goes by in the notes. Bare 'vLLM' is
# deliberately not an alias anywhere: it means upstream vLLM, not the plugin.
PROSE_ALIASES = ['MTPLX']

RELEASE_FEED = {'repo': 'youssofal/MTPLX', 'scheme': 'release', 'note': ''}

WHAT = ('An MLX runtime built around one idea: run the multi-token-prediction heads a model '
 'already ships, instead of a second draft model. The head drafts K tokens, the target '
 'verifies the block in one batched forward pass, and acceptance is Leviathan-and-Chen '
 'rejection sampling with residual correction, so the output distribution is unchanged at '
 'real sampling settings. That narrows what it will load to almost nothing: '
 '`mtplx/backends/registry.py` is an explicit architecture catalog with a per-family tensor '
 'gate, and anything outside it is refused rather than run badly. Most MLX conversions on '
 'the hub drop the draft tensors and zero `num_nextn_predict_layers`, so the usual outcome '
 'even for a supported family is autoregressive decoding with an "unverified" label - the '
 'engine is only interesting where a first-party artifact or your own Forge build carries '
 'the head. Apple silicon only, macOS 14+; Apache-2.0 with a NOTICE clause that requires '
 'in-product attribution if you redistribute it.')

API_DETAIL = {'endpoints': 'OpenAI: /v1/chat/completions, /v1/completions, /v1/models, and optional '
              '/v1/embeddings and /v1/rerank that serve separate MLX retrieval models. '
              'Anthropic: /v1/messages. Plus /health and /metrics. Binds 127.0.0.1:8000; '
              '`--host 0.0.0.0` and `--api-key-file` are opt-in. There is no /v1/responses '
              'surface; it is an open feature request.',
 'streaming': 'SSE on both the OpenAI and Anthropic surfaces. No periodic keep-alive comment '
              'lines yet, so a long prefill can read-timeout an intermediate proxy, and there '
              'is an open report of turns ending with a spurious '
              '"request cancelled" that nothing cancelled.',
 'tools': 'Tools in both the OpenAI and Anthropic styles. **Tool calls stream incrementally** '
          '- argument bytes go out as `tool_calls[].function.arguments` deltas, and as '
          '`partial_json` on the Anthropic surface. The defect to know about is upstream of '
          'the model: the compact tool contract truncates its declared-tool list at 1200 '
          'characters and drops whatever falls off the end.',
 'structured': '`response_format` with grammar-constrained decoding, and strict tool-call '
               'arguments, landed 2026-07-21. It is not available on every scheduler: '
               '`mtp_batch` rejects `response_format` outright.',
 'concurrency': 'The default scheduler is `serial` - one request at a time. `cooperative`, '
                '`ar_batch` and `mtp_batch` exist and are backend-declared, but batching is '
                'where this engine is weakest: two concurrent requests measured 0.41x the '
                'single-request throughput on an M3 Max, and a preempted 175K-token session '
                'has been reported taking 45 minutes to first token.',
 'gotcha': 'The app is stricter than the engine. It refuses any repository without '
           '`mtplx_runtime.json`, which only `mtplx forge` writes, so no third-party '
           'checkpoint can be added through the UI even when `mtplx inspect` reports '
           '`can_run: true` - and it misreports the refusal as an incomplete download. Every '
           'degraded model below is CLI-only for that reason.'}

# Issues that affect every model on this engine.
CROSS_ISSUES = ['youssofal/MTPLX#348',
 'youssofal/MTPLX#383',
 'youssofal/MTPLX#323',
 'youssofal/MTPLX#359',
 'youssofal/MTPLX#376',
 'youssofal/MTPLX#343',
 'youssofal/MTPLX#360',
 'youssofal/MTPLX#358']

# Quant family this engine loads.
QUANT_FAMILY = 'mlx'
