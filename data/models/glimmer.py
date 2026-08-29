"""Muse Glimmer 30B - model record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'glimmer'
MODALITY = 'text'
NAME = 'Muse Glimmer 30B'
ARCH = 'Dense 30B · multimodal (text + image)'
LICENSE = 'Apache-2.0'
CONTEXT = '131k'
HF = 'meta-models/Muse-Glimmer-30B'
PARAMS_B = 30

NOTE = ("Meta's open agentic model, distilled from the closed Muse Spark - Spark itself is API-only, "
 'so this is the one you can actually run. Apache-2.0, with Meta publishing both the GGUF and '
 'a draft head, and mlx-community carrying a 4/5/6/8-bit family. It leads MCP Atlas at 75.5 '
 "and posts SWE-bench Verified 76.0, but its Terminal-Bench 2.1 of 51.7 trails Qwen3.8-27B's "
 '73.0, so it is stronger at tool orchestration than at raw terminal work. One caution for '
 'agent use: Siren AgentDojo puts its prompt-injection attack-success rate at 28.4%.')

SOURCES = [('Meta AI Research announcement',
  'https://research.meta.ai/blog/introducing-muse-glimmer-open-agentic-model'),
 ('Artificial Analysis benchmarks', 'https://artificialanalysis.ai/articles/muse-glimmer'),
 ('Model card', 'https://huggingface.co/meta-models/Muse-Glimmer-30B')]

SCORES = {'agentic': [('MCP Atlas', '75.5'),
             ('DeepSearch QA', '74.6'),
             ('OSWorld-Verified', '65.9'),
             ('GAIA2', '43.3'),
             ('Terminal-Bench 2.1', '51.7')],
 'coding': [('SWE-bench Verified', '76.0'), ('SWE-bench Pro', '51.2')]}

# Which engine the card opens on and the glance row names.
BEST_ENGINE = 'llamacpp'

# Repositories tracker/measure.py harvests for this model.
QUANT_SOURCES = {'gguf': ['unsloth/Muse-Glimmer-30B-GGUF'],
 'mlx': ['mlx-community/Muse-Glimmer-30B-8bit',
         'mlx-community/Muse-Glimmer-30B-6bit',
         'mlx-community/Muse-Glimmer-30B-4bit',
         'mlx-community/Muse-Glimmer-30B-mxfp4']}

# Measured by tracker/measure.py - do not hand-edit. gb is summed repo bytes;
# bpw is gb*8/PARAMS_B and is omitted for pruned or native-precision builds.
LADDER = {'gguf': [{'bpw': 14.86,
           'gb': 55.7,
           'kind': 'quant',
           'label': 'Muse-Glimmer-30B-BF16',
           'repo': 'unsloth/Muse-Glimmer-30B-GGUF'},
          {'bpw': 7.9,
           'gb': 29.6,
           'kind': 'quant',
           'label': 'Muse-Glimmer-30B-Q8_0',
           'repo': 'unsloth/Muse-Glimmer-30B-GGUF'},
          {'bpw': 7.0,
           'gb': 26.3,
           'kind': 'quant',
           'label': 'Muse-Glimmer-30B-UD-Q6_K_XL',
           'repo': 'unsloth/Muse-Glimmer-30B-GGUF'},
          {'bpw': 5.81,
           'gb': 21.8,
           'kind': 'quant',
           'label': 'Muse-Glimmer-30B-UD-Q5_K_XL',
           'repo': 'unsloth/Muse-Glimmer-30B-GGUF'},
          {'bpw': 5.12,
           'gb': 19.2,
           'kind': 'quant',
           'label': 'Muse-Glimmer-30B-UD-Q5_K_M',
           'repo': 'unsloth/Muse-Glimmer-30B-GGUF'},
          {'bpw': 3.77,
           'gb': 14.1,
           'kind': 'quant',
           'label': 'Muse-Glimmer-30B-UD-IQ3_M',
           'repo': 'unsloth/Muse-Glimmer-30B-GGUF'},
          {'bpw': 3.56,
           'gb': 13.4,
           'kind': 'quant',
           'label': 'Muse-Glimmer-30B-UD-Q3_K_XL',
           'repo': 'unsloth/Muse-Glimmer-30B-GGUF'},
          {'bpw': 3.32,
           'gb': 12.4,
           'kind': 'quant',
           'label': 'Muse-Glimmer-30B-UD-Q2_K_XL',
           'repo': 'unsloth/Muse-Glimmer-30B-GGUF'},
          {'bpw': 2.87,
           'gb': 10.7,
           'kind': 'quant',
           'label': 'Muse-Glimmer-30B-UD-IQ2_XXS',
           'repo': 'unsloth/Muse-Glimmer-30B-GGUF'}],
 'mlx': [{'bpw': 8.9,
          'gb': 33.38,
          'kind': 'quant',
          'label': 'Muse-Glimmer-30B-8bit',
          'repo': 'mlx-community/Muse-Glimmer-30B-8bit'},
         {'bpw': 7.04,
          'gb': 26.4,
          'kind': 'quant',
          'label': 'Muse-Glimmer-30B-6bit',
          'repo': 'mlx-community/Muse-Glimmer-30B-6bit'},
         {'bpw': 5.18,
          'gb': 19.41,
          'kind': 'quant',
          'label': 'Muse-Glimmer-30B-4bit',
          'repo': 'mlx-community/Muse-Glimmer-30B-4bit'},
         {'bpw': 4.94,
          'gb': 18.54,
          'kind': 'quant',
          'label': 'Muse-Glimmer-30B-mxfp4',
          'repo': 'mlx-community/Muse-Glimmer-30B-mxfp4'}]}

# Bytes of KV per token at fp16, the context ceiling, and how it was derived.
# None for models with no growing cache (diffusion, TTS).
KV = {'bytes_per_token': 13312,
 'max_context': 131072,
 'derivation': '13 of 52 layers are full attention; the other 39 are windowed at 2048'}

# Per-engine status. Keys must be engines whose modality matches MODALITY.
ENGINES = {'llamacpp': {'status': 'works',
              'label': 'Runs',
              'note': 'Meta publishes the GGUF itself, alongside an mmproj for vision and a '
                      '1.6 GB dflash draft head for speculative decoding. Two caveats that '
                      'both matter for agents: a roughly 50 KB request has been reported to '
                      'kill llama-server outright, and the draft head fails to bind on builds '
                      'that encode a sliding-window key.',
              'issues': ['ggml-org/llama.cpp#27427',
                         'ggml-org/llama.cpp#26894',
                         'ggml-org/llama.cpp#27066']},
 'ollama': {'status': 'works',
            'label': 'Runs',
            'note': 'In the library with a full tag ladder from 17 GB to 57 GB. Nothing '
                    'model-specific to work around.',
            'issues': []},
 'lmstudio': {'status': 'works',
              'label': 'Runs',
              'note': 'Curated in both formats. Given that the MLX path has live tool-calling '
                      'and speculative-decoding reports and the GGUF path does not, being able '
                      'to switch engines without changing tools is worth something here.',
              'issues': []},
 'omlx': {'status': 'degraded',
          'label': 'Runs, degraded',
          'note': 'It loads and it is fast in principle, but the open reports cluster on '
                  'precisely what you would buy Glimmer for. Tool calling has been reported '
                  'broken on the oQ4e checkpoint, and DFlash speculative decoding both '
                  'disables the prefix cache and can end a turn after reasoning without '
                  'emitting the forced call. Run it with DFlash off and check which quant you '
                  'pulled.',
          'issues': ['jundot/omlx#2589',
                     'jundot/omlx#2600',
                     'jundot/omlx#2604',
                     'jundot/omlx#2641']},
 'vllmmlx': {'status': 'works',
             'label': 'Runs',
             'note': 'A clean pairing: zero open muse_glimmer issues in mlx-lm, a full '
                     'mlx-community quant family at 4/5/6/8-bit, and a dense 30B that needs '
                     'none of the hybrid-attention machinery that breaks elsewhere on this '
                     'engine.',
             'issues': []},
 'mlxlm': {'status': 'works',
           'label': 'Runs',
           'note': 'muse_glimmer has no open issues in mlx-lm. This is the quiet reference '
                   'path for the model.',
           'issues': ['ml-explore/mlx-lm#1335']},
 'vllmmetal': {'status': 'blocked',
               'label': 'Blocked',
               'note': 'Not in the support matrix. The project asks that unsupported models be '
                       'raised as issues rather than assumed, which is a reasonable read on '
                       'how narrow the tested set is.',
               'issues': []},
 'ds4': {'status': 'none',
         'label': 'Out of scope',
         'note': 'Not one of the three checkpoints ds4 loads.',
         'issues': []},
 'mtplx': {'status': 'none',
           'label': 'Out of scope',
           'note': 'No MTP head in the checkpoint and no `muse_glimmer` entry in the '
                   'architecture catalog, so it is refused before loading. Meta does publish a '
                   'separate draft head, and that does not help: MTPLX will not pair an '
                   'arbitrary drafter with a trunk, on the stated grounds that nothing in the '
                   'tensor shapes proves the two were trained together. Its one paired backend '
                   'is the first-party Gemma 4 bundle. Use one of the general-purpose MLX '
                   'servers for this model.',
           'issues': []}}
