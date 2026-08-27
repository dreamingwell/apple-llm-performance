"""vllm-mlx - engine record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'vllmmlx'
NAME = 'vllm-mlx'
# Tab position on every card. Explicit so adding an engine cannot silently
# reshuffle the others; leave gaps of 10 to make insertion cheap.
DISPLAY_ORDER = 60
MODALITIES = ['text']
FORMAT = 'MLX'
INTERFACE = 'Server'
API = 'OpenAI and Anthropic'
LICENSE = 'Apache-2.0'
REPO = 'waybarrios/vllm-mlx'

# Canonical website, linked wherever this engine is named in prose.
SITE = 'https://github.com/waybarrios/vllm-mlx'

# The names this engine actually goes by in the notes. Bare 'vLLM' is
# deliberately not an alias anywhere: it means upstream vLLM, not the plugin.
PROSE_ALIASES = ['vllm-mlx']

RELEASE_FEED = {'repo': 'waybarrios/vllm-mlx', 'scheme': 'release', 'note': ''}

WHAT = ("A paged KV cache and continuous batching over mlx-lm's model classes. Unaffiliated with "
 'vllm-project/vllm despite the name. Because it wraps mlx-lm rather than reimplementing '
 "models, an architecture missing upstream is missing here, and mlx-lm's bugs arrive intact.")

API_DETAIL = {'endpoints': 'OpenAI: /v1/chat/completions, /v1/completions, /v1/embeddings, /v1/rerank, '
              '/v1/responses. Anthropic: /v1/messages with streaming, tool use and system '
              'prompts. Prometheus /metrics.',
 'streaming': 'Yes on both surfaces. Usage is reported, but `cached_tokens` is not surfaced '
              'yet - an open PR - so you cannot see prefix-cache hits from the API.',
 'tools': '19 tool parsers (OpenAI, Anthropic, Gemini, Qwen, DeepSeek, Gemma and more) plus '
          'reasoning parsers selected with `--reasoning-parser`.',
 'structured': '`response_format` with `json_schema`.',
 'concurrency': 'The strongest story on paper: continuous batching over a paged KV cache with '
                'prefix caching and SSD tiering, which is the whole reason the project exists.',
 'gotcha': 'Three open defects land squarely on the streaming path: streamed tool calls can '
           'end without a `finish_reason`, closing a stream mid-flight leaves the generator '
           'and request state open, and a strict `json_schema` decode can wedge. Also bind '
           'carefully - non-loopback requests have been reported silently dropped on 0.0.0.0.'}

# Issues that affect every model on this engine.
CROSS_ISSUES = ['waybarrios/vllm-mlx#619',
 'waybarrios/vllm-mlx#584',
 'waybarrios/vllm-mlx#672',
 'waybarrios/vllm-mlx#546',
 'waybarrios/vllm-mlx#627',
 'waybarrios/vllm-mlx#682',
 'waybarrios/vllm-mlx#732',
 'waybarrios/vllm-mlx#570']

# Quant family this engine loads.
QUANT_FAMILY = 'mlx'
