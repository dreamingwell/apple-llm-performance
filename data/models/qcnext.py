"""Qwen3-Coder-Next - model record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'qcnext'
MODALITY = 'text'
NAME = 'Qwen3-Coder-Next'
ARCH = 'MoE 80B total / 3B active · 12 Gated Attention + 36 Gated DeltaNet layers'
LICENSE = 'Apache-2.0'
CONTEXT = '262k'
HF = 'Qwen/Qwen3-Coder-Next'
PARAMS_B = 80

NOTE = ('The best fit-to-capability ratio on this page. 3B active out of 80B total gets SWE-bench '
 'Verified 74.2% - within a point of GLM-5.2 at a fraction of the footprint - and '
 'Apache-2.0 with a 38-tier GGUF ladder means it runs on almost anything. Note the caveats: '
 'its Terminal-Bench figure is on v2.0, so it cannot be ranked against the v2.1 numbers '
 'elsewhere here, and it is non-thinking only. KV is 24 KiB/token, among the cheapest here, so '
 'long context is affordable.')

SOURCES = [('Model card', 'https://huggingface.co/Qwen/Qwen3-Coder-Next'),
 ('Qwen blog', 'https://qwen.ai/blog?id=qwen3-coder-next')]

SCORES = {'agentic': [('Terminal-Bench 2.0', '36.2')],
 'coding': [('SWE-bench Verified', '74.2%'),
            ('SWE-bench Multilingual', '63.7%'),
            ('Aider', '66.2')]}

# Which engine the card opens on and the glance row names.
BEST_ENGINE = 'llamacpp'

# Repositories tracker/measure.py harvests for this model.
QUANT_SOURCES = {'gguf': ['unsloth/Qwen3-Coder-Next-GGUF'],
 'mlx': ['mlx-community/Qwen3-Coder-Next-8bit',
         'mlx-community/Qwen3-Coder-Next-6bit',
         'mlx-community/Qwen3-Coder-Next-5bit',
         'mlx-community/Qwen3-Coder-Next-4bit',
         'nightmedia/Qwen3-Coder-Next-mxfp4-mlx']}

# Measured by tracker/measure.py - do not hand-edit. gb is summed repo bytes;
# bpw is gb*8/PARAMS_B and is omitted for pruned or native-precision builds.
LADDER = {'gguf': [{'bpw': 15.95,
           'gb': 159.5,
           'kind': 'quant',
           'label': 'Qwen3-Coder-Next-BF16',
           'repo': 'unsloth/Qwen3-Coder-Next-GGUF'},
          {'bpw': 7.31,
           'gb': 73.1,
           'kind': 'quant',
           'label': 'Qwen3-Coder-Next-UD-Q6_K_XL',
           'repo': 'unsloth/Qwen3-Coder-Next-GGUF'},
          {'bpw': 5.68,
           'gb': 56.8,
           'kind': 'quant',
           'label': 'Qwen3-Coder-Next-Q5_K_M',
           'repo': 'unsloth/Qwen3-Coder-Next-GGUF'},
          {'bpw': 4.61,
           'gb': 46.1,
           'kind': 'quant',
           'label': 'Qwen3-Coder-Next-UD-Q4_K_S',
           'repo': 'unsloth/Qwen3-Coder-Next-GGUF'},
          {'bpw': 3.92,
           'gb': 39.2,
           'kind': 'quant',
           'label': 'Qwen3-Coder-Next-UD-IQ4_NL',
           'repo': 'unsloth/Qwen3-Coder-Next-GGUF'},
          {'bpw': 3.46,
           'gb': 34.6,
           'kind': 'quant',
           'label': 'Qwen3-Coder-Next-Q3_K_S',
           'repo': 'unsloth/Qwen3-Coder-Next-GGUF'},
          {'bpw': 2.85,
           'gb': 28.5,
           'kind': 'quant',
           'label': 'Qwen3-Coder-Next-UD-IQ3_XXS',
           'repo': 'unsloth/Qwen3-Coder-Next-GGUF'},
          {'bpw': 2.33,
           'gb': 23.3,
           'kind': 'quant',
           'label': 'Qwen3-Coder-Next-UD-IQ2_XXS',
           'repo': 'unsloth/Qwen3-Coder-Next-GGUF'},
          {'bpw': 1.89,
           'gb': 18.9,
           'kind': 'quant',
           'label': 'Qwen3-Coder-Next-UD-TQ1_0',
           'repo': 'unsloth/Qwen3-Coder-Next-GGUF'}],
 'mlx': [{'bpw': 8.47,
          'gb': 84.66,
          'kind': 'quant',
          'label': 'Qwen3-Coder-Next-8bit',
          'repo': 'mlx-community/Qwen3-Coder-Next-8bit'},
         {'bpw': 6.47,
          'gb': 64.75,
          'kind': 'quant',
          'label': 'Qwen3-Coder-Next-6bit',
          'repo': 'mlx-community/Qwen3-Coder-Next-6bit'},
         {'bpw': 5.48,
          'gb': 54.8,
          'kind': 'quant',
          'label': 'Qwen3-Coder-Next-5bit',
          'repo': 'mlx-community/Qwen3-Coder-Next-5bit'},
         {'bpw': 4.48,
          'gb': 44.84,
          'kind': 'quant',
          'label': 'Qwen3-Coder-Next-4bit',
          'repo': 'mlx-community/Qwen3-Coder-Next-4bit'},
         {'bpw': 4.24,
          'gb': 42.36,
          'kind': 'quant',
          'label': 'Qwen3-Coder-Next-mxfp4-mlx',
          'repo': 'nightmedia/Qwen3-Coder-Next-mxfp4-mlx'}]}

# Bytes of KV per token at fp16, the context ceiling, and how it was derived.
# None for models with no growing cache (diffusion, TTS).
KV = {'bytes_per_token': 24576,
 'max_context': 262144,
 'derivation': '12 of 48 layers are Gated Attention; the other 36 are Gated DeltaNet, which '
               'holds a fixed state'}

# Per-engine status. Keys must be engines whose modality matches MODALITY.
ENGINES = {'llamacpp': {'status': 'works',
              'label': 'Runs',
              'note': '`qwen3next` is in mainline, and unsloth publishes the deepest quant '
                      'ladder of any model here - 38 tiers from 18.9 GB to 159.5 GB - so this '
                      'fits almost any Mac at a precision you choose rather than one you '
                      'accept. 3B active means decode stays cheap even on a laptop. Watch one '
                      'report of garbled output, though it is filed against an abliterated '
                      'finetune rather than the base weights.',
              'issues': ['ggml-org/llama.cpp#27727']},
 'ollama': {'status': 'works',
            'label': 'Runs',
            'note': '`ollama run qwen3-coder-next`. Given the 3B active parameters and 256k '
                    'context, this is the closest thing on the page to a drop-in local coding '
                    'agent.',
            'issues': []},
 'lmstudio': {'status': 'works',
              'label': 'Runs',
              'note': 'Curated in both formats under lmstudio-community - GGUF plus MLX at 4, '
                      '6 and 8-bit - which makes it one of the better-served models in the '
                      'catalogue.',
              'issues': []},
 'omlx': {'status': 'degraded',
          'label': 'Runs, degraded',
          'note': "oMLX's own README uses this model in its example model directory, so it is "
                  "a supported path. Two things to know: mlx-lm's hybrid cache is reported "
                  'silently broken for Qwen3-Next, which removes prefix reuse without telling '
                  'you, and continuous-batching prefill has been reported collapsing at '
                  'exactly two concurrent requests.',
          'issues': ['ml-explore/mlx-lm#1162', 'jundot/omlx#1783', 'jundot/omlx#2252']},
 'vllmmlx': {'status': 'degraded',
             'label': 'Runs, degraded',
             'note': "Loads on mlx-lm's qwen3_next class. The hybrid-cache defect upstream is "
                     'the thing to check first, because a silently broken prompt cache costs '
                     'you the whole reason to run a server.',
             'issues': ['ml-explore/mlx-lm#1162']},
 'mlxlm': {'status': 'degraded',
           'label': 'Runs, degraded',
           'note': '`qwen3_next.py` exists and generates. The hybrid cache silently failing is '
                   'filed here and propagates to every MLX server that wraps it.',
           'issues': ['ml-explore/mlx-lm#1162', 'ml-explore/mlx-lm#1335']},
 'vllmmetal': {'status': 'works',
               'label': 'Runs',
               'note': 'Qwen3-Next is a supported family with its own row in the matrix, on '
                       'the same hybrid SDPA + GDN path as Qwen3.8. Prefix caching is opt-in '
                       "for that shape. At 3B active this is a natural fit for vLLM's "
                       'continuous batching.',
               'issues': ['vllm-project/vllm-metal#610', 'vllm-project/vllm-metal#646']},
 'ds4': {'status': 'none',
         'label': 'Out of scope',
         'note': 'Not one of the three checkpoints ds4 loads.',
         'issues': []},
 'mtplx': {'status': 'degraded',
           'label': 'Runs, no MTP',
           'note': 'Recognised as the Qwen3-Next family, so it loads and serves - but every '
                   'mlx-community build measured above has zero `mtp.*` tensors and no '
                   '`num_nextn_predict_layers` in its config, which puts it on the `mtp_heads '
                   'not found -> mtp_off` path: autoregressive decode with an "unverified" '
                   'label. That is the same speed any other MLX server gives you, without the '
                   'hybrid cache reuse those servers at least attempt. To get the draft head '
                   'you would build the artifact yourself with `mtplx forge` from the BF16 '
                   'weights, and note that Forge has an open failure on official Qwen '
                   'checkpoints. Until then this is a runtime you are paying for and not using.',
           'issues': ['youssofal/MTPLX#299']}}
