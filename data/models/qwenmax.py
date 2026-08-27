"""Qwen3.8-Max - model record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'qwenmax'
MODALITY = 'text'
NAME = 'Qwen3.8-Max'
ARCH = 'MoE 2.45T total / 95B active · hybrid GDN (23 full-attn + 69 linear of 92)'
LICENSE = 'Qwen3.8-Max (custom)'
CONTEXT = '262k'
HF = 'Qwen/Qwen3.8-2.4T-A95B'
PARAMS_B = 2446

NOTE = ('The weights are public at Qwen/Qwen3.8-2.4T-A95B and the architecture is already supported - '
 'this is the same qwen3_5_moe family as Qwen3.8-27B, so llama.cpp and mlx-lm both load it. '
 'Terminal-Bench 2.1 of 86.6 is second only to Kimi K3 on this page, and its SWE-bench Pro of '
 '67.7 leads it outright. What stops it is arithmetic: 2.45T parameters means the smallest '
 'unpruned build is 397 GB at 1.30 bits per weight, and the first tier clearing 2 bits is 656 '
 'GB. Everything that fits a realistic Mac has either been quantised past the point its own '
 'quantiser warns about, or had most of its experts deleted.')

SOURCES = [('Model card with full tables', 'https://huggingface.co/Qwen/Qwen3.8-2.4T-A95B')]

SCORES = {'agentic': [('Terminal-Bench 2.1', '86.6'),
             ('CoWorkBench', '74.8'),
             ('Toolathlon Verified', '72.5'),
             ('JobBench', '53.4')],
 'coding': [('SWE-bench Pro', '67.7'),
            ('QwenSWEBench', '80.7'),
            ('FrontierSWE', '73.5'),
            ('DeepSWE 1.1', '56.6')]}

# Which engine the card opens on and the glance row names.
BEST_ENGINE = 'llamacpp'

# Repositories tracker/measure.py harvests for this model.
QUANT_SOURCES = {'gguf': ['unsloth/Qwen3.8-2.4T-A95B-GGUF',
          'hellohazime/Qwen3.8-2.4T-A95B-REAP-512GB-GGUF',
          'hellohazime/Qwen3.8-2.4T-A95B-REAP-256GB-GGUF'],
 'mlx': ['kernelpool/Qwen3.8-2.4T-A95B-3bit-UVMAX',
         'pipenetwork/Qwen3.8-2.4T-A95B-MLX-reap50-3bit',
         'pipenetwork/Qwen3.8-2.4T-A95B-MLX-reap60-3bit',
         'pipenetwork/Qwen3.8-2.4T-A95B-MLX-reap75-4bit']}

# Measured by tracker/measure.py - do not hand-edit. gb is summed repo bytes;
# bpw is gb*8/PARAMS_B and is omitted for pruned or native-precision builds.
LADDER = {'gguf': [{'bpw': 16.0,
           'gb': 4893.2,
           'kind': 'quant',
           'label': 'Qwen3.8-2.4T-A95B-BF16',
           'repo': 'unsloth/Qwen3.8-2.4T-A95B-GGUF'},
          {'bpw': 8.5,
           'gb': 2600.2,
           'kind': 'quant',
           'label': 'Qwen3.8-2.4T-A95B-Q8_0',
           'repo': 'unsloth/Qwen3.8-2.4T-A95B-GGUF'},
          {'bpw': 4.29,
           'gb': 1310.9,
           'kind': 'quant',
           'label': 'Qwen3.8-2.4T-A95B-UD-IQ4_XS',
           'repo': 'unsloth/Qwen3.8-2.4T-A95B-GGUF'},
          {'bpw': 2.39,
           'gb': 730.7,
           'kind': 'quant',
           'label': 'Qwen3.8-2.4T-A95B-UD-IQ2_XS',
           'repo': 'unsloth/Qwen3.8-2.4T-A95B-GGUF'},
          {'bpw': 2.15,
           'gb': 656.6,
           'kind': 'quant',
           'label': 'Qwen3.8-2.4T-A95B-UD-IQ2_XXS',
           'repo': 'unsloth/Qwen3.8-2.4T-A95B-GGUF'},
          {'bpw': 1.84,
           'gb': 564.0,
           'kind': 'quant',
           'label': 'Qwen3.8-2.4T-A95B-UD-IQ1_M',
           'repo': 'unsloth/Qwen3.8-2.4T-A95B-GGUF'},
          {'bpw': None,
           'gb': 404.2,
           'kind': 'pruned',
           'label': 'Qwen3.8-2.4T-A95B-REAP-512GB-IQ2_XXS',
           'repo': 'hellohazime/Qwen3.8-2.4T-A95B-REAP-512GB-GGUF'},
          {'bpw': 1.3,
           'gb': 397.3,
           'kind': 'quant',
           'label': 'Qwen3.8-2.4T-A95B-UD-Q1_0',
           'repo': 'unsloth/Qwen3.8-2.4T-A95B-GGUF'},
          {'bpw': None,
           'gb': 246.2,
           'kind': 'pruned',
           'label': 'Qwen3.8-2.4T-A95B-REAP-256GB-IQ1_S',
           'repo': 'hellohazime/Qwen3.8-2.4T-A95B-REAP-256GB-GGUF'}],
 'mlx': [{'bpw': 2.63,
          'gb': 805.62,
          'kind': 'quant',
          'label': 'Qwen3.8-2.4T-A95B-3bit-UVMAX',
          'repo': 'kernelpool/Qwen3.8-2.4T-A95B-3bit-UVMAX'},
         {'bpw': None,
          'gb': 540.28,
          'kind': 'pruned',
          'label': 'Qwen3.8-2.4T-A95B-MLX-reap50-3bit',
          'repo': 'pipenetwork/Qwen3.8-2.4T-A95B-MLX-reap50-3bit'},
         {'bpw': None,
          'gb': 436.88,
          'kind': 'pruned',
          'label': 'Qwen3.8-2.4T-A95B-MLX-reap60-3bit',
          'repo': 'pipenetwork/Qwen3.8-2.4T-A95B-MLX-reap60-3bit'},
         {'bpw': None,
          'gb': 360.94,
          'kind': 'pruned',
          'label': 'Qwen3.8-2.4T-A95B-MLX-reap75-4bit',
          'repo': 'pipenetwork/Qwen3.8-2.4T-A95B-MLX-reap75-4bit'}]}

# Bytes of KV per token at fp16, the context ceiling, and how it was derived.
# None for models with no growing cache (diffusion, TTS).
KV = {'bytes_per_token': 94208,
 'max_context': 262144,
 'derivation': '23 of 92 layers are full attention, one in every 4; the other 69 are linear'}

# Per-engine status. Keys must be engines whose modality matches MODALITY.
ENGINES = {'llamacpp': {'status': 'works',
              'label': 'Runs',
              'note': 'The weights are public at `Qwen/Qwen3.8-2.4T-A95B` and the architecture '
                      'is `qwen3_5_moe`, which llama.cpp already implements as `qwen35moe` - '
                      'the same family as Qwen3.8-27B. So this is purely a capacity problem, '
                      'not a support one. The ladder is brutal: UD-IQ4_XS is 1.31 TB, '
                      'UD-IQ2_XXS is 656.6 GB, and the smallest unpruned build is UD-Q1_0 at '
                      '397.3 GB. Someone has also published REAP-pruned GGUFs sized '
                      'deliberately for 256 GB and 512 GB Macs.',
              'issues': []},
 'ollama': {'status': 'blocked',
            'label': 'Not in library',
            'note': 'The `qwen3.8` library entry carries only 27B tags. Nothing at this size '
                    'is published, which is reasonable - a 397 GB minimum does not suit a '
                    'one-command pull.',
            'issues': []},
 'lmstudio': {'status': 'works',
              'label': 'Runs',
              'note': 'Through the llama.cpp engine on the GGUF ladder. Nothing curated under '
                      'lmstudio-community at this size, so you are pointing it at a community '
                      'repo.',
              'issues': []},
 'omlx': {'status': 'degraded',
          'label': 'Pruned builds only',
          'note': "mlx-lm's `qwen3_5_moe` class covers the architecture, so this loads - but "
                  'every published MLX build except one is REAP expert-pruned, and the one '
                  'that is not is 805.6 GB. At these sizes the load-time watchdog on >300 GB '
                  'checkpoints is also in play.',
          'issues': ['ml-explore/mlx-lm#1572', 'jundot/omlx#2307']},
 'vllmmlx': {'status': 'degraded',
             'label': 'Pruned builds only',
             'note': 'Same picture as oMLX: the class exists, the unpruned MLX build is 805.6 '
                     'GB, and everything smaller has had experts deleted.',
             'issues': ['ml-explore/mlx-lm#1572']},
 'mlxlm': {'status': 'degraded',
           'label': 'Pruned builds only',
           'note': '`qwen3_5_moe.py` handles it. The constraint is what has been published: '
                   'pruned builds from 360.9 GB up, or 805.6 GB unpruned.',
           'issues': ['ml-explore/mlx-lm#1572', 'ml-explore/mlx-lm#1446']},
 'vllmmetal': {'status': 'degraded',
               'label': 'Untested at this size',
               'note': 'The matrix row covering Qwen3.5/3.6/3.8 notes that the 3.6 generation '
                       'adds MoE, so this architecture is plausibly in scope - but nobody has '
                       'run a 2.45T checkpoint through it, and no MLX build of this model '
                       'exists that is not expert-pruned. Treat it as untested rather than '
                       'supported.',
               'issues': ['ml-explore/mlx-lm#1572']},
 'ds4': {'status': 'none',
         'label': 'Out of scope',
         'note': 'Not one of the three checkpoints ds4 loads.',
         'issues': []}}
