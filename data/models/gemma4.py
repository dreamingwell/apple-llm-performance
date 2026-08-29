"""Gemma 4 31B - model record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'gemma4'
MODALITY = 'text'
NAME = 'Gemma 4 31B'
ARCH = 'Dense 30.7B · also E2B / E4B / 26B-A4B variants'
LICENSE = 'Apache-2.0'
CONTEXT = '256k'
HF = 'google/gemma-4-31b-it'
PARAMS_B = 30.7

NOTE = ('The clearest case on this page for looking past MLX. τ²-Bench 86.4% is the second-highest '
 'tool-use number here, Google publishes a quantisation-aware-trained q4_0 GGUF itself at 17.7 '
 'GB, and llama.cpp, Ollama and LM Studio all load it today. The MLX side is the worst on this '
 'page, and the weights are not why - 4-bit and QAT 4-bit conversions of the 31B both exist. '
 'It carries more open mlx-lm issues than any other architecture tracked here, which is '
 'exactly the sort of gap that makes an MLX-only view of Apple Silicon misleading.')

SOURCES = [('Benchmark writeup', 'https://codersera.com/blog/gemma-4-complete-guide-2026/'),
 ('SWE-bench detail', 'https://www.gemma4.wiki/benchmark/gemma-4-swe-bench')]

SCORES = {'agentic': [('τ²-Bench', '86.4%')],
 'coding': [('SWE-bench Verified', '52.0%'),
            ('LiveCodeBench-v6', '80.0%'),
            ('SWE-bench Pro', '35.7%')]}

# Which engine the card opens on and the glance row names.
BEST_ENGINE = 'llamacpp'

# Repositories tracker/measure.py harvests for this model.
QUANT_SOURCES = {'gguf': ['unsloth/gemma-4-31B-it-GGUF'],
 'mlx': ['mlx-community/gemma-4-31b-it-8bit',
         'mlx-community/gemma-4-31B-it-qat-4bit',
         'mlx-community/gemma-4-31b-it-4bit']}

# Measured by tracker/measure.py - do not hand-edit. gb is summed repo bytes;
# bpw is gb*8/PARAMS_B and is omitted for pruned or native-precision builds.
LADDER = {'gguf': [{'bpw': 16.0,
           'gb': 61.4,
           'kind': 'quant',
           'label': 'gemma-4-31B-it-BF16',
           'repo': 'unsloth/gemma-4-31B-it-GGUF'},
          {'bpw': 8.5,
           'gb': 32.6,
           'kind': 'quant',
           'label': 'gemma-4-31B-it-Q8_0',
           'repo': 'unsloth/gemma-4-31B-it-GGUF'},
          {'bpw': 6.57,
           'gb': 25.2,
           'kind': 'quant',
           'label': 'gemma-4-31B-it-Q6_K',
           'repo': 'unsloth/gemma-4-31B-it-GGUF'},
          {'bpw': 5.5,
           'gb': 21.1,
           'kind': 'quant',
           'label': 'gemma-4-31B-it-Q5_K_S',
           'repo': 'unsloth/gemma-4-31B-it-GGUF'},
          {'bpw': 4.77,
           'gb': 18.3,
           'kind': 'quant',
           'label': 'gemma-4-31B-it-Q4_K_M',
           'repo': 'unsloth/gemma-4-31B-it-GGUF'},
          {'bpw': 4.27,
           'gb': 16.4,
           'kind': 'quant',
           'label': 'gemma-4-31B-it-IQ4_XS',
           'repo': 'unsloth/gemma-4-31B-it-GGUF'},
          {'bpw': 3.84,
           'gb': 14.7,
           'kind': 'quant',
           'label': 'gemma-4-31B-it-Q3_K_M',
           'repo': 'unsloth/gemma-4-31B-it-GGUF'},
          {'bpw': 3.08,
           'gb': 11.8,
           'kind': 'quant',
           'label': 'gemma-4-31B-it-UD-IQ3_XXS',
           'repo': 'unsloth/gemma-4-31B-it-GGUF'},
          {'bpw': 2.22,
           'gb': 8.5,
           'kind': 'quant',
           'label': 'gemma-4-31B-it-UD-IQ2_XXS',
           'repo': 'unsloth/gemma-4-31B-it-GGUF'}],
 'mlx': [{'bpw': 8.8,
          'gb': 33.76,
          'kind': 'quant',
          'label': 'gemma-4-31b-it-8bit',
          'repo': 'mlx-community/gemma-4-31b-it-8bit'},
         {'bpw': 7.51,
          'gb': 28.82,
          'kind': 'quant',
          'label': 'gemma-4-31B-it-qat-4bit',
          'repo': 'mlx-community/gemma-4-31B-it-qat-4bit'},
         {'bpw': 4.8,
          'gb': 18.41,
          'kind': 'quant',
          'label': 'gemma-4-31b-it-4bit',
          'repo': 'mlx-community/gemma-4-31b-it-4bit'}]}

# Bytes of KV per token at fp16, the context ceiling, and how it was derived.
# None for models with no growing cache (diffusion, TTS).
KV = {'bytes_per_token': 163840,
 'max_context': 262144,
 'derivation': '10 of 60 layers are full attention, the rest windowed at 1024'}

# Per-engine status. Keys must be engines whose modality matches MODALITY.
ENGINES = {'llamacpp': {'status': 'works',
              'label': 'Runs',
              'note': 'This is the model the MLX-only view of the world gets most wrong. '
                      'Google publishes a quantisation-aware-trained q4_0 GGUF itself - 17.7 '
                      'GB, plus a 1.2 GB mmproj for vision - so the recommended download comes '
                      "from the model's own authors and QAT means less quality lost than a "
                      'post-hoc 4-bit. Two things to know: sliding-window attention has a '
                      'report of dropping earlier context, which matters because SWA is how '
                      'the 256k window is built, and MTP speculative decoding crashes today.',
              'issues': ['ggml-org/llama.cpp#25751',
                         'ggml-org/llama.cpp#25522',
                         'ggml-org/llama.cpp#25739']},
 'ollama': {'status': 'works',
            'label': 'Runs',
            'note': '`ollama run gemma4`, with a tag ladder from 10 GB to 24 GB. The single '
                    'easiest way to get the highest tool-use score on this page running on a '
                    'Mac.',
            'issues': ['ollama/ollama#17783']},
 'lmstudio': {'status': 'works',
              'label': 'Runs',
              'note': 'The QAT build is curated under lmstudio-community. Either engine can '
                       'serve this - the GGUF ladder is the finer-grained one, and 4-bit MLX '
                       'builds of the 31B do exist - but the MLX side inherits the open mlx-lm '
                       'defects listed on the mlx-lm tab, so GGUF is the safer default.',
              'issues': []},
 'omlx': {'status': 'degraded',
          'label': 'Runs, degraded',
          'note': 'oMLX has real Gemma 4 traffic - a Gemma tool parser, and open reports of a '
                   'post-0.6.1 performance regression, a practical context wall well short of '
                   'the advertised 256k, and DFlash disabling the prefix cache. Weights are not '
                   'the problem: mlx-community ships a 4-bit of the 31B at 18.4 GB and a QAT '
                   '4-bit at 28.8 GB. The problem is underneath, on an mlx-lm path with more '
                   'open issues than any other architecture tracked here.',
          'issues': ['jundot/omlx#2786',
                     'jundot/omlx#1794',
                     'jundot/omlx#2600',
                     'ml-explore/mlx-lm#1493',
                     'ml-explore/mlx-lm#1352']},
 'vllmmlx': {'status': 'blocked',
             'label': 'Blocked',
             'note': 'The worst MLX story on the page, and not for want of weights - mlx- '
                      'community publishes both a 4-bit and a QAT 4-bit of the 31B. gemma4 '
                      'carries more open mlx-lm issues than any other architecture here: '
                      'generation hangs at 0% CPU right after prompt processing, thinking- '
                      'enabled turns come back with reasoning and empty content, one variant '
                      'will not load at all, and RotatingKVCache blocks `--kv-bits` on the '
                      'sliding-window layers this model is built from.',
             'issues': ['ml-explore/mlx-lm#1493',
                        'ml-explore/mlx-lm#1352',
                        'ml-explore/mlx-lm#1242',
                        'waybarrios/vllm-mlx#590',
                        'ml-explore/mlx-lm#1573']},
 'mlxlm': {'status': 'blocked',
           'label': 'Blocked',
           'note': 'Same blockers, one layer down. These are the issues every MLX server '
                   'inherits.',
           'issues': ['ml-explore/mlx-lm#1493',
                      'ml-explore/mlx-lm#1352',
                      'ml-explore/mlx-lm#1242',
                      'ml-explore/mlx-lm#1573']},
 'vllmmetal': {'status': 'works',
               'label': 'Runs',
               'note': 'Fully supported, with a Metal kernel for its per-layer sliding window '
                       'and YOCO, and automatic prefix caching on by default rather than '
                       'opt-in. That makes this the cleanest MLX route to Gemma 4 by a '
                       'distance - mlx-lm cannot load the 31B at all. The example checkpoint '
                       'in the matrix is the small E2B variant, so verify the 31B before '
                       'planning around it.',
               'issues': []},
 'ds4': {'status': 'none',
         'label': 'Out of scope',
         'note': 'Not one of the three checkpoints ds4 loads.',
         'issues': []}}
