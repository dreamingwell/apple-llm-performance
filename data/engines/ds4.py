"""DwarfStar (ds4) - engine record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'ds4'
NAME = 'DwarfStar (ds4)'
# Tab position on every card. Explicit so adding an engine cannot silently
# reshuffle the others; leave gaps of 10 to make insertion cheap.
DISPLAY_ORDER = 80
MODALITIES = ['text']
FORMAT = 'purpose-built GGUF'
INTERFACE = 'CLI + ds4-server + built-in agent'
API = 'OpenAI and Anthropic'
LICENSE = 'MIT'
REPO = 'antirez/ds4'

# Canonical website, linked wherever this engine is named in prose.
SITE = 'https://github.com/antirez/ds4'

# The names this engine actually goes by in the notes. Bare 'vLLM' is
# deliberately not an alias anywhere: it means upstream vLLM, not the plugin.
PROSE_ALIASES = ['DwarfStar', 'ds4']

RELEASE_FEED = {'repo': 'antirez/ds4',
 'scheme': 'none',
 'note': 'untagged by design (ds4#839); build from main'}

WHAT = ('A single-purpose C and Metal engine for DeepSeek V4 Flash, DeepSeek V4 PRO and GLM-5.2 - '
 'deliberately not a general GGUF loader, so only the published checkpoints load. In exchange '
 'it gets a disk KV cache that persists sessions across restarts, resident session batching, '
 'SSD expert streaming for machines too small to hold the weights, and tensor parallelism '
 'across two Macs over Thunderbolt RDMA. Where it applies, it is the fastest option here.')

API_DETAIL = {'endpoints': 'OpenAI: /v1/models, /v1/models/{alias}, /v1/chat/completions, /v1/completions, '
              '/v1/responses. Anthropic: /v1/messages. The model aliases are compatibility '
              'only - they all report whatever GGUF was passed with `-m`.',
 'streaming': 'SSE on the chat, Responses and Anthropic surfaces, with '
              '`stream_options.include_usage`. In thinking mode reasoning streams on its own '
              'channel instead of being mixed into the final text, and the Responses surface '
              'emits the full Codex event lifecycle - `response.output_text.delta`, '
              'function-call argument events, and terminal `response.completed` / `incomplete` '
              '/ `failed`.',
 'tools': '`tools` and `tool_choice` on all three surfaces. Schemas are rendered into '
          "DeepSeek's DSML format and generated calls mapped back. **Tool calls stream "
          'incrementally**: the header goes out as soon as the DSML invocation is recognised, '
          'then argument bytes are forwarded as `tool_calls[].function.arguments` deltas while '
          'generation continues.',
 'structured': 'No `response_format` or grammar support; correctness comes from DSML '
               'canonicalisation rather than constrained decoding.',
 'concurrency': '`--batched-session N` preallocates N resident KV sessions with fair '
                'scheduling, and idle slots persist to the disk KV cache before reuse. MTP '
                'speculative decoding is disabled while native session batching is active.',
 'gotcha': 'The best streaming implementation here, from the narrowest engine - but stateless '
           'clients have been reported failing to extend the live KV session on Flash/Metal, '
           'which quietly removes the prefix reuse that is the main reason to run it. Add '
           '`--cors` for browser clients; `--host 0.0.0.0` is opt-in.'}

# Issues that affect every model on this engine.
CROSS_ISSUES = ['antirez/ds4#853',
 'antirez/ds4#816',
 'antirez/ds4#836',
 'antirez/ds4#805',
 'antirez/ds4#845',
 'antirez/ds4#839',
 'antirez/ds4#860']

# Quant family this engine loads.
QUANT_FAMILY = 'ds4'
