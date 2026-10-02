"""gpt-oss-120b - model record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'gptoss'
MODALITY = 'text'
NAME = 'gpt-oss-120b'
ARCH = 'MoE 120B total / ~5.1B active'
LICENSE = 'Apache-2.0'
CONTEXT = '128k'
HF = 'openai/gpt-oss-120b'
PARAMS_B = 120
# Parameters read per decoded token, the divisor in the decode ceiling:
# published as ~5.1B active of 120B total.
ACTIVE_PARAMS_B = 5.1

NOTE = ('Older now, but a genuinely comfortable fit on any engine: 5.1B active means fast decode and '
 '63-66 GB leaves plenty of KV room. Scores scale with reasoning effort - the figures shown '
 'are the high setting; medium gives SWE-bench 52.6% and τ-Bench Retail 62.0%. Apache-2.0. Its '
 'one recurring problem is not the model but Harmony: the channel format its tool calls ride '
 'on has open parsing defects in more than one engine.')

SOURCES = [('Model card / paper', 'https://arxiv.org/html/2508.10925v1'),
 ('OpenAI announcement', 'https://openai.com/index/introducing-gpt-oss/')]

SCORES = {'agentic': [('τ-Bench Retail (high)', '67.8%'), ('τ-Bench Airline (high)', '49.2%')],
 'coding': [('SWE-bench Verified (high)', '62.4%'), ('Codeforces', '2622 Elo')]}

# Which engine the card opens on and the glance row names.
BEST_ENGINE = 'llamacpp'

# Repositories tracker/measure.py harvests for this model.
QUANT_SOURCES = {'gguf': ['ggml-org/gpt-oss-120b-GGUF'],
 'mlx': ['lmstudio-community/gpt-oss-120b-MLX-8bit',
         'inferencerlabs/openai-gpt-oss-120b-MLX-Q6',
         'mlx-community/gpt-oss-120b-MXFP4-Q8']}

# Measured by tracker/measure.py - do not hand-edit. gb is summed repo bytes;
# bpw is gb*8/PARAMS_B and is omitted for pruned or native-precision builds.
LADDER = {'gguf': [{'bpw': 4.23,
           'gb': 63.4,
           'kind': 'quant',
           'label': 'gpt-oss-120b-MXFP4',
           'repo': 'ggml-org/gpt-oss-120b-GGUF'}],
 'mlx': [{'bpw': 8.28,
          'gb': 124.17,
          'kind': 'quant',
          'label': 'gpt-oss-120b-MLX-8bit',
          'repo': 'lmstudio-community/gpt-oss-120b-MLX-8bit'},
         {'bpw': 6.33,
          'gb': 94.97,
          'kind': 'quant',
          'label': 'openai-gpt-oss-120b-MLX-Q6',
          'repo': 'inferencerlabs/openai-gpt-oss-120b-MLX-Q6'},
         {'bpw': 4.23,
          'gb': 63.39,
          'kind': 'quant',
          'label': 'gpt-oss-120b-MXFP4-Q8',
          'repo': 'mlx-community/gpt-oss-120b-MXFP4-Q8'}]}

# Bytes of KV per token at fp16, the context ceiling, and how it was derived.
# None for models with no growing cache (diffusion, TTS).
KV = {'bytes_per_token': 36864,
 'max_context': 131072,
 'derivation': '18 of 36 layers are full attention, alternating with a 128-token window'}

# Per-engine status. Keys must be engines whose modality matches MODALITY.
ENGINES = {'llamacpp': {'status': 'degraded',
              'label': 'Runs, degraded',
              'note': "63.4 GB in OpenAI's native MXFP4, from ggml-org, plus an EAGLE3 draft "
                      'model. It runs well; both open problems are in the agent path rather '
                      'than the model. A large tool list can generate a GBNF grammar that '
                      'fails to parse, and malformed Harmony channel headers drop tool calls.',
              'issues': ['ggml-org/llama.cpp#25967', 'ggml-org/llama.cpp#27720']},
 'ollama': {'status': 'works',
            'label': 'Runs',
            'note': '`ollama run gpt-oss:120b`. One of the better-exercised models in the '
                    'library.',
            'issues': []},
 'lmstudio': {'status': 'works',
              'label': 'Runs',
              'note': 'Curated in both formats. 5.1B active keeps decode fast on either '
                      'engine.',
              'issues': []},
 'omlx': {'status': 'degraded',
          'label': 'Runs, degraded',
          'note': 'Loads comfortably - 65.8 GB leaves plenty of KV room - but the Harmony '
                  'plumbing has open defects that specifically cost tool calls: '
                  'correctly-formed calls addressed to `functions.*` have been dropped by a '
                  'stricter channel check, and there is a report of the OpenAI endpoint 500ing '
                  'while the Anthropic endpoint on the same server works.',
          'issues': ['jundot/omlx#2216', 'jundot/omlx#2018']},
 'vllmmlx': {'status': 'works',
             'label': 'Runs',
             'note': 'A genuinely comfortable fit: 5.1B active means fast decode, 65.8 GB '
                     'leaves plenty of KV room, and the gpt_oss path in mlx-lm is quiet.',
             'issues': []},
 'mlxlm': {'status': 'works',
           'label': 'Runs',
           'note': "Quiet on the model side. Harmony parsing is the client's problem here "
                   "rather than the engine's.",
           'issues': []},
 'vllmmetal': {'status': 'works',
               'label': 'Runs, experimental',
               'note': 'Listed as experimental, with a dedicated sink-attention kernel and '
                       'automatic prefix caching. gpt-oss is a shape that trips several '
                       'engines on this page, so a purpose-built attention path for it is '
                       'worth something.',
               'issues': ['vllm-project/vllm-metal#646']},
 'ds4': {'status': 'none',
         'label': 'Out of scope',
         'note': 'Not one of the three checkpoints ds4 loads.',
         'issues': []}}
