"""GLM-4.7-Flash - model record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'glm47f'
MODALITY = 'text'
NAME = 'GLM-4.7-Flash'
ARCH = 'MoE 31B total / ~3B active'
LICENSE = 'MIT'
CONTEXT = '131k'
HF = 'zai-org/GLM-4.7-Flash'
PARAMS_B = 31

NOTE = ('3B active out of 31B, so decode is bandwidth-cheap and KV space is abundant - the opposite '
 'tradeoff to the large GLM tiers, on the same MIT license. The natural cheap tier to route '
 'low-stakes work to, and the easiest thing on this page to get running on any engine.')

SOURCES = [('Model card (all scores)', 'https://huggingface.co/zai-org/GLM-4.7-Flash')]

SCORES = {'agentic': [('τ²-Bench', '79.5%'), ('BrowseComp', '42.8%')],
 'coding': [('SWE-bench Verified', '59.2%'), ('LiveCodeBench-v6', '64.0%')]}

# Which engine the card opens on and the glance row names.
BEST_ENGINE = 'llamacpp'

# Repositories tracker/measure.py harvests for this model.
QUANT_SOURCES = {'gguf': ['unsloth/GLM-4.7-Flash-GGUF'],
 'mlx': ['mlx-community/GLM-4.7-Flash-8bit',
         'mlx-community/GLM-4.7-Flash-6bit',
         'mlx-community/GLM-4.7-Flash-5bit',
         'mlx-community/GLM-4.7-Flash-4bit']}

# Measured by tracker/measure.py - do not hand-edit. gb is summed repo bytes;
# bpw is gb*8/PARAMS_B and is omitted for pruned or native-precision builds.
LADDER = {'gguf': [{'bpw': 15.46,
           'gb': 59.9,
           'kind': 'quant',
           'label': 'GLM-4.7-Flash-BF16',
           'repo': 'unsloth/GLM-4.7-Flash-GGUF'},
          {'bpw': 6.75,
           'gb': 26.2,
           'kind': 'quant',
           'label': 'GLM-4.7-Flash-UD-Q6_K_XL',
           'repo': 'unsloth/GLM-4.7-Flash-GGUF'},
          {'bpw': 5.6,
           'gb': 21.7,
           'kind': 'quant',
           'label': 'GLM-4.7-Flash-UD-Q5_K_XL',
           'repo': 'unsloth/GLM-4.7-Flash-GGUF'},
          {'bpw': 4.73,
           'gb': 18.3,
           'kind': 'quant',
           'label': 'GLM-4.7-Flash-Q4_K_M',
           'repo': 'unsloth/GLM-4.7-Flash-GGUF'},
          {'bpw': 4.2,
           'gb': 16.3,
           'kind': 'quant',
           'label': 'GLM-4.7-Flash-IQ4_XS',
           'repo': 'unsloth/GLM-4.7-Flash-GGUF'},
          {'bpw': 3.43,
           'gb': 13.3,
           'kind': 'quant',
           'label': 'GLM-4.7-Flash-Q3_K_S',
           'repo': 'unsloth/GLM-4.7-Flash-GGUF'},
          {'bpw': 2.95,
           'gb': 11.4,
           'kind': 'quant',
           'label': 'GLM-4.7-Flash-Q2_K_L',
           'repo': 'unsloth/GLM-4.7-Flash-GGUF'},
          {'bpw': 2.71,
           'gb': 10.5,
           'kind': 'quant',
           'label': 'GLM-4.7-Flash-UD-IQ2_XXS',
           'repo': 'unsloth/GLM-4.7-Flash-GGUF'},
          {'bpw': 2.15,
           'gb': 8.3,
           'kind': 'quant',
           'label': 'GLM-4.7-Flash-UD-TQ1_0',
           'repo': 'unsloth/GLM-4.7-Flash-GGUF'}],
 'mlx': [{'bpw': 8.21,
          'gb': 31.82,
          'kind': 'quant',
          'label': 'GLM-4.7-Flash-8bit',
          'repo': 'mlx-community/GLM-4.7-Flash-8bit'},
         {'bpw': 6.28,
          'gb': 24.34,
          'kind': 'quant',
          'label': 'GLM-4.7-Flash-6bit',
          'repo': 'mlx-community/GLM-4.7-Flash-6bit'},
         {'bpw': 5.31,
          'gb': 20.59,
          'kind': 'quant',
          'label': 'GLM-4.7-Flash-5bit',
          'repo': 'mlx-community/GLM-4.7-Flash-5bit'},
         {'bpw': 4.35,
          'gb': 16.85,
          'kind': 'quant',
          'label': 'GLM-4.7-Flash-4bit',
          'repo': 'mlx-community/GLM-4.7-Flash-4bit'}]}

# Bytes of KV per token at fp16, the context ceiling, and how it was derived.
# None for models with no growing cache (diffusion, TTS).
KV = {'bytes_per_token': 54144,
 'max_context': 202752,
 'derivation': '47 layers of latent attention, kv_lora_rank 512 + 64 rope'}

# Per-engine status. Keys must be engines whose modality matches MODALITY.
ENGINES = {'llamacpp': {'status': 'works',
              'label': 'Runs',
              'note': "First-class: the GGUF lives in ggml-org's own namespace, which is as "
                      'strong a support signal as this ecosystem gives. 18.2 GB at Q4_K, 31.8 '
                      'GB at Q8_0, and enough headroom on any machine here that quantisation '
                      'choice is about quality rather than fit.',
              'issues': []},
 'ollama': {'status': 'works',
            'label': 'Runs',
            'note': '`ollama run glm-4.7-flash`. The easiest thing on this page to get '
                    'running, and small enough that the default tag is the right tag.',
            'issues': []},
 'lmstudio': {'status': 'works',
              'label': 'Runs',
              'note': 'Curated in both formats under lmstudio-community, MLX at 6-bit and '
                      '8-bit included. A good place to measure what the MLX-versus-GGUF gap '
                      'actually is on your machine, since both builds are one click apart.',
              'issues': []},
 'omlx': {'status': 'works',
          'label': 'Runs',
          'note': 'The best match on this page for what oMLX is for. 3B active makes decode '
                  'cheap, 16.9 GB leaves the rest of the machine for KV blocks, and continuous '
                  'batching plus the hot/cold cache is exactly the shape of a high-concurrency '
                  'cheap tier.',
          'issues': ['jundot/omlx#2307']},
 'vllmmlx': {'status': 'works',
             'label': 'Runs',
             'note': '3B active, so decode is bandwidth-cheap and KV space is abundant - the '
                     'opposite tradeoff to the large GLM tiers, on the same mature code path '
                     'and quant family.',
             'issues': ['waybarrios/vllm-mlx#725']},
 'mlxlm': {'status': 'works',
           'label': 'Runs',
           'note': 'Works, and small enough that the CLI is a reasonable way to use it rather '
                   'than just to test it.',
           'issues': ['ml-explore/mlx-lm#1335']},
 'vllmmetal': {'status': 'works',
               'label': 'Runs, experimental',
               'note': 'Experimental but on the plain GQA paged path with automatic prefix '
                       "caching, and `mlx-community/GLM-4.7-Flash-4bit` is the matrix's own "
                       "example checkpoint. 3B active over vLLM's continuous batching is a "
                       'good pairing.',
               'issues': ['vllm-project/vllm-metal#646']},
 'ds4': {'status': 'none',
         'label': 'Out of scope',
         'note': 'Not one of the three checkpoints ds4 loads.',
         'issues': []}}
