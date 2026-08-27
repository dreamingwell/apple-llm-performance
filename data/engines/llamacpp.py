"""llama.cpp - engine record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'llamacpp'
NAME = 'llama.cpp'
# Tab position on every card. Explicit so adding an engine cannot silently
# reshuffle the others; leave gaps of 10 to make insertion cheap.
DISPLAY_ORDER = 10
MODALITIES = ['text']
FORMAT = 'GGUF'
INTERFACE = 'CLI + llama-server'
API = 'OpenAI-compatible'
LICENSE = 'MIT'
REPO = 'ggml-org/llama.cpp'

# Canonical website, linked wherever this engine is named in prose.
SITE = 'https://github.com/ggml-org/llama.cpp'

# The names this engine actually goes by in the notes. Bare 'vLLM' is
# deliberately not an alias anywhere: it means upstream vLLM, not the plugin.
PROSE_ALIASES = ['llama.cpp']

RELEASE_FEED = {'repo': 'ggml-org/llama.cpp',
 'scheme': 'semver',
 'note': 'also publishes hourly b##### builds'}

WHAT = ('The reference GGUF runtime, with a first-class Metal backend. New architectures land here '
 'earlier and more completely than anywhere else on this page, and Ollama, LM Studio, Jan, '
 'KoboldCpp and most other local runners are downstream of it. `llama-server` exposes an '
 'OpenAI-compatible endpoint, so nothing here is GUI-only.')

API_DETAIL = {'endpoints': 'OpenAI: /v1/models, /v1/chat/completions, /v1/completions, /v1/responses, '
              '/v1/embeddings, plus token-counting routes for chat and responses. Anthropic: '
              '/v1/messages and /v1/messages/count_tokens. Also /slots prompt-cache '
              'save/restore, Prometheus /metrics, and real-time completion control.',
 'streaming': 'SSE on every chat surface. Returns a standard `usage` object plus a `timings` '
              'block that reports `cache_n` - how many prompt tokens were reused from cache - '
              'which is the number you want when tuning an agent loop.',
 'tools': 'Native tool-call styles per model family with a generic fallback, `tool_choice`, '
          'and `parallel_tool_calls` gated on what the jinja template supports. Arguments '
          'stream as deltas.',
 'structured': '`response_format` accepts both `json_object` and `json_schema`, enforced by '
               'GBNF grammar sampling at the token level rather than validated afterwards.',
 'concurrency': 'Parallel slots (`-np`), with per-slot prompt caches you can persist to disk.',
 'gotcha': 'Tool use requires the `--jinja` flag on both the OpenAI and Anthropic surfaces - '
           "without it `tools` is silently inert. The project's own docs decline to claim spec "
           'compliance: “no strong claims of compatibility with OpenAI API spec is being '
           'made”.'}

# Issues that affect every model on this engine.
CROSS_ISSUES = ['ggml-org/llama.cpp#25967',
 'ggml-org/llama.cpp#27427',
 'ggml-org/llama.cpp#26382',
 'ggml-org/llama.cpp#26894']

# Quant family this engine loads.
QUANT_FAMILY = 'gguf'
