"""LM Studio - engine record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'lmstudio'
NAME = 'LM Studio'
# Tab position on every card. Explicit so adding an engine cannot silently
# reshuffle the others; leave gaps of 10 to make insertion cheap.
DISPLAY_ORDER = 30
MODALITIES = ['text']
FORMAT = 'GGUF and MLX'
INTERFACE = 'Desktop app + `lms` CLI + server'
API = 'OpenAI-compatible on :1234'
LICENSE = 'Proprietary, free to use'
REPO = None

# Canonical website, linked wherever this engine is named in prose.
SITE = 'https://lmstudio.ai'

# The names this engine actually goes by in the notes. Bare 'vLLM' is
# deliberately not an alias anywhere: it means upstream vLLM, not the plugin.
PROSE_ALIASES = ['LM Studio']

RELEASE_FEED = {'repo': None,
 'scheme': 'none',
 'note': 'closed source; no public tag feed, see the in-app release notes'}

WHAT = ('App-first but not app-only. It ships both a llama.cpp engine and its own MLX engine, so for '
 'any given model it can take whichever path works, and its catalogue tends to carry a curated '
 'quant within a day of a release. The `lms` CLI and the server run headless.')

API_DETAIL = {'endpoints': 'OpenAI: /v1/models, /v1/chat/completions, /v1/completions, /v1/responses, '
              '/v1/embeddings. Its own REST API and TypeScript/Python SDKs are more capable '
              'than the compatibility layer.',
 'streaming': 'Yes. Tool calls stream properly as `delta.tool_calls[].function.arguments` '
              'fragments you accumulate across chunks - the correct OpenAI shape.',
 'tools': 'Standard OpenAI tool schemas, with per-family native formats and a documented '
          'generic fallback for models with no native tool support.',
 'structured': '`json_schema` only - **`json_object` mode is not supported**. Enforcement '
               'differs by engine: llama.cpp grammars for GGUF, Outlines for MLX. SDK '
               'integrations bind to Zod, Pydantic and msgspec.',
 'concurrency': 'Serves multiple requests; models load and unload through the app or `lms`.',
 'gotcha': 'The two engines are not equivalent through the same API. An open report has the '
           'MLX engine silently clamping context to 4864 tokens and ignoring every override, '
           'which surfaces as the model being bad rather than the server being wrong.'}

# Issues that affect every model on this engine.
CROSS_ISSUES = ['lmstudio-ai/lmstudio-bug-tracker#2323',
 'lmstudio-ai/lmstudio-bug-tracker#2273',
 'lmstudio-ai/lmstudio-bug-tracker#2265',
 'lmstudio-ai/lmstudio-bug-tracker#2240',
 'lmstudio-ai/lmstudio-bug-tracker#2243',
                 'lmstudio-ai/lmstudio-bug-tracker#2324']

# Quant family this engine loads.
QUANT_FAMILY = 'gguf'
