"""GLM-4.7 - model record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'glm47'
MODALITY = 'text'
NAME = 'GLM-4.7'
ARCH = 'MoE 358B total / ~32B active · conventional attention'
LICENSE = 'MIT'
CONTEXT = '131k'
HF = 'zai-org/GLM-4.7'
PARAMS_B = 358

NOTE = ('The strongest model that fits a single 256 GB machine without heroics, MIT-licensed, and the '
 'only one on this page that every engine here can load. What varies is the fit: llama.cpp '
 'reaches a 158.7 GB Q3 tier while the MLX 4-bit is 198.6 GB, which on one box is the '
 'difference between a usable context and a token budget. It uses conventional attention '
 'rather than hybrid linear attention, which is why it avoids the class of cache bug that dogs '
 'Qwen3.8-27B.')

SOURCES = [('Model card (all scores)', 'https://huggingface.co/zai-org/GLM-4.7')]

SCORES = {'agentic': [('τ²-Bench', '87.4%'), ('BrowseComp', '67.5%'), ('Terminal-Bench 2.0', '41.0%')],
 'coding': [('SWE-bench Verified', '73.8%'),
            ('LiveCodeBench-v6', '84.9%'),
            ('SWE-bench Multilingual', '66.7%')]}

# Which engine the card opens on and the glance row names.
BEST_ENGINE = 'llamacpp'

# Repositories tracker/measure.py harvests for this model.
QUANT_SOURCES = {'gguf': ['unsloth/GLM-4.7-GGUF'],
 'mlx': ['mlx-community/GLM-4.7-8bit',
         'mlx-community/GLM-4.7-6bit',
         'mlx-community/GLM-4.7-4bit',
         'mlx-community/GLM-4.7-REAP-50-mxfp4']}

# Measured by tracker/measure.py - do not hand-edit. gb is summed repo bytes;
# bpw is gb*8/PARAMS_B and is omitted for pruned or native-precision builds.
LADDER = {'gguf': [{'bpw': 16.02,
           'gb': 716.8,
           'kind': 'quant',
           'label': 'GLM-4.7-BF16',
           'repo': 'unsloth/GLM-4.7-GGUF'},
          {'bpw': 8.51,
           'gb': 381.0,
           'kind': 'quant',
           'label': 'GLM-4.7-Q8_0',
           'repo': 'unsloth/GLM-4.7-GGUF'},
          {'bpw': 5.68,
           'gb': 254.2,
           'kind': 'quant',
           'label': 'GLM-4.7-Q5_K_M',
           'repo': 'unsloth/GLM-4.7-GGUF'},
          {'bpw': 4.84,
           'gb': 216.5,
           'kind': 'quant',
           'label': 'GLM-4.7-Q4_K_M',
           'repo': 'unsloth/GLM-4.7-GGUF'},
          {'bpw': 4.28,
           'gb': 191.6,
           'kind': 'quant',
           'label': 'GLM-4.7-IQ4_XS',
           'repo': 'unsloth/GLM-4.7-GGUF'},
          {'bpw': 3.24,
           'gb': 145.1,
           'kind': 'quant',
           'label': 'GLM-4.7-UD-IQ3_XXS',
           'repo': 'unsloth/GLM-4.7-GGUF'},
          {'bpw': 2.74,
           'gb': 122.4,
           'kind': 'quant',
           'label': 'GLM-4.7-UD-IQ2_M',
           'repo': 'unsloth/GLM-4.7-GGUF'},
          {'bpw': 2.41,
           'gb': 107.7,
           'kind': 'quant',
           'label': 'GLM-4.7-UD-IQ1_M',
           'repo': 'unsloth/GLM-4.7-GGUF'},
          {'bpw': 1.89,
           'gb': 84.5,
           'kind': 'quant',
           'label': 'GLM-4.7-UD-TQ1_0',
           'repo': 'unsloth/GLM-4.7-GGUF'}],
 'mlx': [{'bpw': 8.38,
          'gb': 374.92,
          'kind': 'quant',
          'label': 'GLM-4.7-8bit',
          'repo': 'mlx-community/GLM-4.7-8bit'},
         {'bpw': 6.41,
          'gb': 286.74,
          'kind': 'quant',
          'label': 'GLM-4.7-6bit',
          'repo': 'mlx-community/GLM-4.7-6bit'},
         {'bpw': 4.44,
          'gb': 198.56,
          'kind': 'quant',
          'label': 'GLM-4.7-4bit',
          'repo': 'mlx-community/GLM-4.7-4bit'},
         {'bpw': None,
          'gb': 98.22,
          'kind': 'pruned',
          'label': 'GLM-4.7-REAP-50-mxfp4',
          'repo': 'mlx-community/GLM-4.7-REAP-50-mxfp4'}]}

# Bytes of KV per token at fp16, the context ceiling, and how it was derived.
# None for models with no growing cache (diffusion, TTS).
KV = {'bytes_per_token': 376832,
 'max_context': 202752,
 'derivation': '92 layers x 8 KV heads x 128, full attention throughout'}

# Per-engine status. Keys must be engines whose modality matches MODALITY.
ENGINES = {'llamacpp': {'status': 'works',
              'label': 'Runs',
              'note': 'The best fit of any engine for this model, because llama.cpp has quant '
                      "tiers MLX does not. UD-Q3_K_XL is 158.7 GB against the MLX 4-bit's "
                      '198.6 GB, which turns a 21 GB KV budget into about 60 GB on the same '
                      'machine - the difference between a demo and a working context. IQ4_XS '
                      '(191.6 GB) and UD-Q4_K_XL (204.6 GB) sit either side of the MLX build '
                      'if you would rather spend the memory on weights. No open '
                      'GLM-4.7-specific Metal issues.',
              'issues': []},
 'ollama': {'status': 'works',
            'label': 'Runs',
            'note': '`ollama run glm-4.7` works, but the default tag is a Q4-class build near '
                    '205 GB, which leaves almost nothing for KV on a 256 GB machine. Pull an '
                    'explicit smaller tag rather than the default if you are on one box. Note '
                    'that on Apple Silicon Ollama now routes through MLX by default, so which '
                    'path you get depends on what the tag ships.',
            'issues': []},
 'lmstudio': {'status': 'works',
              'label': 'Runs',
              'note': 'The one engine that can pick per model: load the GGUF Q3 tier for '
                      'headroom or the mlx-community 4-bit for speed, from the same app, and '
                      'compare them without changing tools. Serves on :1234 for any OpenAI '
                      'client.',
              'issues': []},
 'omlx': {'status': 'works',
          'label': 'Runs',
          'note': "glm4_moe is a mature mlx-lm path and oMLX's GLM tool parser is explicitly "
                  'implemented, so this is a comfortable pairing - you get continuous batching '
                  'and the SSD KV tier on top. The constraint is arithmetic, not software: '
                  '198.6 GB of weights on a 256 GB box leaves about 21 GB for KV, and the SSD '
                  'cold tier is what makes that survivable.',
          'issues': ['jundot/omlx#2307']},
 'vllmmlx': {'status': 'works',
             'label': 'Runs',
             'note': 'The original recommendation on this page and still a good one. glm4_moe '
                     'has zero open issues in mlx-lm - every one closed - and it uses '
                     'conventional attention rather than hybrid linear attention, so it should '
                     'sidestep the prefix-cache bug that cripples Qwen3.8-27B on this engine. '
                     'Confirm that first; it is the main reason to prefer it here.',
             'issues': ['waybarrios/vllm-mlx#725']},
 'mlxlm': {'status': 'works',
           'label': 'Runs',
           'note': 'Loads and generates. Use it to establish what the model does correctly '
                   'before adding a serving layer, then move to one of the servers above for '
                   'concurrency.',
           'issues': ['ml-explore/mlx-lm#1335']},
 'vllmmetal': {'status': 'blocked',
               'label': 'Blocked',
               'note': 'The support matrix lists GLM-4.7-Flash but not the full 358B model, '
                       'and the GLM-4.5 row it does carry is flagged as MLA with no Metal '
                       'kernel and untested. This is a curated matrix rather than a general '
                       'loader, so absence means absence.',
               'issues': ['vllm-project/vllm-metal#360']},
 'ds4': {'status': 'none',
         'label': 'Out of scope',
         'note': 'ds4 loads DeepSeek V4 Flash, DeepSeek V4 PRO and GLM-5.2 only. GLM-4.7 is a '
                 'different architecture and will not load.',
         'issues': []}}
