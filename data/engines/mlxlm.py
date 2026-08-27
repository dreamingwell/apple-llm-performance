"""mlx-lm - engine record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'mlxlm'
NAME = 'mlx-lm'
# Tab position on every card. Explicit so adding an engine cannot silently
# reshuffle the others; leave gaps of 10 to make insertion cheap.
DISPLAY_ORDER = 70
MODALITIES = ['text']
FORMAT = 'MLX'
INTERFACE = 'CLI + `mlx_lm.server`'
API = 'OpenAI-compatible, minimal'
LICENSE = 'MIT'
REPO = 'ml-explore/mlx-lm'

# Canonical website, linked wherever this engine is named in prose.
SITE = 'https://github.com/ml-explore/mlx-lm'

# The names this engine actually goes by in the notes. Bare 'vLLM' is
# deliberately not an alias anywhere: it means upstream vLLM, not the plugin.
PROSE_ALIASES = ['mlx-lm']

RELEASE_FEED = {'repo': 'ml-explore/mlx-lm', 'scheme': 'release', 'note': ''}

WHAT = ("Apple's own reference implementation, and the substrate almost everything MLX-shaped depends "
 'on. Treat it as the floor: an architecture with no model class here is absent from most of '
 'the MLX ecosystem at once. The bundled server is deliberately basic - one model, simple '
 'batching - so it is a correctness reference more than a serving layer.')

API_DETAIL = {'endpoints': 'OpenAI: POST /v1/chat/completions (and bare /chat/completions), POST '
              '/v1/completions, GET /v1/models, GET /health. No embeddings, no rerank, no '
              'responses.',
 'streaming': 'Yes, SSE, with `stream_options.include_usage` and `prompt_tokens_details` for '
              'cached prompt tokens.',
 'tools': '`tool_calls` are parsed and returned. It also implements `logprobs` and '
          '`top_logprobs` up to 11, which Ollama does not - a genuine inversion of the usual '
          'ordering.',
 'structured': '**None.** There is no `response_format`, no `json_schema` and no grammar '
               'support anywhere in the server. If your agent depends on constrained decoding, '
               'this engine cannot give it to you.',
 'concurrency': "A ThreadingHTTPServer over mlx-lm's BatchGenerator, but batching is switched "
                'off whenever a draft model is loaded or a `seed` is set - so speculative '
                'decoding and concurrency are mutually exclusive here.',
 'gotcha': 'Better than its reputation on the basics and thinner than expected on structured '
           'output. Treat it as a correctness reference rather than a serving layer.'}

# Issues that affect every model on this engine.
CROSS_ISSUES = ['ml-explore/mlx-lm#1662', 'ml-explore/mlx-lm#1335', 'ml-explore/mlx-lm#1572']

# Quant family this engine loads.
QUANT_FAMILY = 'mlx'
