"""oMLX - engine record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'omlx'
NAME = 'oMLX'
# Tab position on every card. Explicit so adding an engine cannot silently
# reshuffle the others; leave gaps of 10 to make insertion cheap.
DISPLAY_ORDER = 40
MODALITIES = ['text']
FORMAT = 'MLX'
INTERFACE = 'Menu-bar app + server'
API = 'OpenAI and Anthropic'
LICENSE = 'Apache-2.0'
REPO = 'jundot/omlx'

# Canonical website, linked wherever this engine is named in prose.
SITE = 'https://github.com/jundot/omlx'

# The names this engine actually goes by in the notes. Bare 'vLLM' is
# deliberately not an alias anywhere: it means upstream vLLM, not the plugin.
PROSE_ALIASES = ['oMLX']

RELEASE_FEED = {'repo': 'jundot/omlx', 'scheme': 'release', 'note': ''}

WHAT = ('MLX serving built for agent clients: continuous batching, a hot/cold KV cache that spills '
 'blocks to SSD and survives a restart, and hand-written Metal kernels for the GLM-5.2, '
 "MiniMax M3 and Qwen3.5 families. Its LLM coverage is mlx-lm's, plus those kernels and its "
 'own additions - install the custom kernels or the affected families fall back silently to a '
 'much slower generic path.')

API_DETAIL = {'endpoints': 'OpenAI: /v1/chat/completions, /v1/completions, /v1/embeddings, /v1/rerank, '
              '/v1/models. Anthropic: /v1/messages, with adaptive thinking.',
 'streaming': 'Yes, including `stream_options.include_usage`, and SSE keep-alives so a long '
              'prefill does not read-timeout the client. It also scales reported token counts '
              "so Claude Code's auto-compact triggers at the right moment on a smaller-context "
              'model.',
 'tools': 'Per-family parsers (Qwen3.5 XML, GLM arg-key/value, MiniMax namespaced, Gemma, '
          'Kimi, Mistral, Longcat). **Tool calls do not stream incrementally** - assistant '
          'text streams while tool markup is suppressed, and structured calls are emitted only '
          'after the completed turn is parsed.',
 'structured': 'JSON schema validation, plus MCP tool integration.',
 'concurrency': 'Continuous batching, default 8 concurrent requests, over a hot/cold KV cache '
                'that spills to SSD and survives a restart.',
 'gotcha': 'The two surfaces are not interchangeable in practice: there is an open report of '
           'the OpenAI endpoint returning 500 while the Anthropic endpoint on the same server '
           'works. A stricter channel check also drops valid gpt-oss calls addressed to '
           '`functions.*`.'}

# Issues that affect every model on this engine.
CROSS_ISSUES = ['jundot/omlx#2307', 'jundot/omlx#2137']

# Quant family this engine loads.
QUANT_FAMILY = 'mlx'
