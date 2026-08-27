"""Ollama - engine record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'ollama'
NAME = 'Ollama'
# Tab position on every card. Explicit so adding an engine cannot silently
# reshuffle the others; leave gaps of 10 to make insertion cheap.
DISPLAY_ORDER = 20
MODALITIES = ['text']
FORMAT = 'MLX on Apple Silicon, GGUF elsewhere'
INTERFACE = 'Background server + CLI'
API = 'OpenAI-compatible, plus its own /api'
LICENSE = 'MIT'
REPO = 'ollama/ollama'

# Canonical website, linked wherever this engine is named in prose.
SITE = 'https://ollama.com'

# The names this engine actually goes by in the notes. Bare 'vLLM' is
# deliberately not an alias anywhere: it means upstream vLLM, not the plugin.
PROSE_ALIASES = ['Ollama']

RELEASE_FEED = {'repo': 'ollama/ollama', 'scheme': 'release', 'note': ''}

WHAT = ('One-command pulls from a curated library, running as a launch-agent server. Since v0.30 (May '
 '2026) MLX is the default engine on Apple Silicon rather than llama.cpp, which is the single '
 "most important thing to know about it here: on a Mac, Ollama inherits MLX's architecture "
 'coverage for the models it serves through that path.')

API_DETAIL = {'endpoints': 'OpenAI: /v1/models, /v1/models/{model}, /v1/chat/completions, /v1/completions, '
              '/v1/embeddings, /v1/responses. Anthropic-compatible surface as well. Its own '
              'richer /api/* routes sit alongside.',
 'streaming': 'Yes, with `stream_options`. The only engine here that publishes an explicit '
              'checkbox matrix of what it does and does not implement, which is worth more '
              'than most of the feature lists.',
 'tools': 'Tools yes, but **`tool_choice` is not implemented** - you cannot force a specific '
          'call or require that one happen. Also missing: `logprobs`, `n`, `logit_bias`, '
          '`user`.',
 'structured': '`response_format` and JSON mode supported.',
 'concurrency': 'Serves concurrently with automatic model loading and unloading.',
 'gotcha': '`/v1/responses` is non-stateful only: no `previous_response_id`, no '
           '`conversation`. And because MLX is now the default engine on Apple Silicon, a tag '
           'can resolve to a different backend than you expect.'}

# Issues that affect every model on this engine.
CROSS_ISSUES = ['ollama/ollama#15813',
 'ollama/ollama#17638',
 'ollama/ollama#17323',
 'ollama/ollama#14116',
 'ollama/ollama#17656',
 'ollama/ollama#17878',
                 'ollama/ollama#17569']

# Quant family this engine loads.
QUANT_FAMILY = 'gguf'
