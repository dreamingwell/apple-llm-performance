"""MiniMax M3 - model record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'm3'
MODALITY = 'text'
NAME = 'MiniMax M3'
ARCH = 'MoE 428B total / 23B active · MiniMax Sparse Attention'
LICENSE = 'MiniMax Community'
CONTEXT = '1M'
HF = 'MiniMaxAI/MiniMax-M3'
PARAMS_B = 428

NOTE = ('SWE-bench Verified 80.5% is the best coding score on this page that fits one 256 GB machine, '
 'and since the architecture reached mainline llama.cpp that is now a real option rather than '
 "a hypothetical. Note its Terminal-Bench 2.1 of 66.0 sits below Qwen3.8-27B's 73.0 despite "
 'being 15x larger, so it is a coding pick rather than an agentic one. The MLX route is a '
 'vision-language checkpoint with open loader problems.')

SOURCES = [('Model card', 'https://huggingface.co/MiniMaxAI/MiniMax-M3'),
 ('Benchmark writeup', 'https://www.morphllm.com/minimax-m3')]

SCORES = {'agentic': [('Terminal-Bench 2.1', '66.0'), ('MCP Atlas', '74.2')],
 'coding': [('SWE-bench Verified', '80.5%'),
            ('SWE-bench Pro', '59.0%'),
            ('SWE-fficiency', '34.8')]}

# Which engine the card opens on and the glance row names.
BEST_ENGINE = 'llamacpp'

# Repositories tracker/measure.py harvests for this model.
QUANT_SOURCES = {'gguf': ['unsloth/MiniMax-M3-GGUF'],
 'mlx': ['pipenetwork/MiniMax-M3-MLX-8bit',
         'pipenetwork/MiniMax-M3-MLX-6bit',
         'mlx-community/MiniMax-M3-4bit',
         'pipenetwork/MiniMax-M3-MLX-mixed-3_6bit']}

# Measured by tracker/measure.py - do not hand-edit. gb is summed repo bytes;
# bpw is gb*8/PARAMS_B and is omitted for pruned or native-precision builds.
LADDER = {'gguf': [{'bpw': 15.93,
           'gb': 852.0,
           'kind': 'quant',
           'label': 'MiniMax-M3-BF16',
           'repo': 'unsloth/MiniMax-M3-GGUF'},
          {'bpw': 7.24,
           'gb': 387.2,
           'kind': 'quant',
           'label': 'MiniMax-M3-UD-Q6_K_XL',
           'repo': 'unsloth/MiniMax-M3-GGUF'},
          {'bpw': 5.95,
           'gb': 318.5,
           'kind': 'quant',
           'label': 'MiniMax-M3-UD-Q5_K_XL',
           'repo': 'unsloth/MiniMax-M3-GGUF'},
          {'bpw': 4.95,
           'gb': 264.9,
           'kind': 'quant',
           'label': 'MiniMax-M3-UD-Q4_K_XL',
           'repo': 'unsloth/MiniMax-M3-GGUF'},
          {'bpw': 4.63,
           'gb': 247.7,
           'kind': 'quant',
           'label': 'MiniMax-M3-UD-Q4_K_S',
           'repo': 'unsloth/MiniMax-M3-GGUF'},
          {'bpw': 3.96,
           'gb': 211.8,
           'kind': 'quant',
           'label': 'MiniMax-M3-UD-IQ4_NL',
           'repo': 'unsloth/MiniMax-M3-GGUF'},
          {'bpw': 3.27,
           'gb': 174.8,
           'kind': 'quant',
           'label': 'MiniMax-M3-UD-IQ3_S',
           'repo': 'unsloth/MiniMax-M3-GGUF'},
          {'bpw': 2.67,
           'gb': 143.0,
           'kind': 'quant',
           'label': 'MiniMax-M3-UD-Q2_K_XL',
           'repo': 'unsloth/MiniMax-M3-GGUF'},
          {'bpw': 2.4,
           'gb': 128.4,
           'kind': 'quant',
           'label': 'MiniMax-M3-UD-IQ1_M',
           'repo': 'unsloth/MiniMax-M3-GGUF'}],
 'mlx': [{'bpw': 8.46,
          'gb': 452.58,
          'kind': 'quant',
          'label': 'MiniMax-M3-MLX-8bit',
          'repo': 'pipenetwork/MiniMax-M3-MLX-8bit'},
         {'bpw': 6.47,
          'gb': 346.1,
          'kind': 'quant',
          'label': 'MiniMax-M3-MLX-6bit',
          'repo': 'pipenetwork/MiniMax-M3-MLX-6bit'},
         {'bpw': 4.51,
          'gb': 241.48,
          'kind': 'quant',
          'label': 'MiniMax-M3-4bit',
          'repo': 'mlx-community/MiniMax-M3-4bit'},
         {'bpw': 3.57,
          'gb': 191.18,
          'kind': 'quant',
          'label': 'MiniMax-M3-MLX-mixed-3_6bit',
          'repo': 'pipenetwork/MiniMax-M3-MLX-mixed-3_6bit'}]}

# Bytes of KV per token at fp16, the context ceiling, and how it was derived.
# None for models with no growing cache (diffusion, TTS).
KV = {'bytes_per_token': 122880,
 'max_context': 1048576,
 'derivation': '60 layers x 4 KV heads x 128, full attention throughout'}

# Per-engine status. Keys must be engines whose modality matches MODALITY.
ENGINES = {'llamacpp': {'status': 'works',
              'label': 'Runs',
              'note': '`minimax-m3` is in mainline llama.cpp, which flips this model from '
                      'unreachable to practical. A 22-tier ladder means you can choose your '
                      'fit: UD-IQ3_XXS at 159.4 GB, UD-Q3_K_XL at 194.9 GB, UD-IQ4_XS at 207.6 '
                      'GB, with the Q4 tiers (248-265 GB) needing more than one 256 GB '
                      'machine. SWE-bench Verified 80.5% is the highest coding score on this '
                      'page that fits a single box.',
              'issues': []},
 'ollama': {'status': 'works',
            'label': 'Runs',
            'note': 'In the library. Check which quant the tag resolves to before pulling 250 '
                    'GB onto a 256 GB machine.',
            'issues': []},
 'lmstudio': {'status': 'works',
              'label': 'Runs',
              'note': 'GGUF path only in practice - the MLX conversion is an mlx-vlm build '
                      "with open loader problems. LM Studio's llama.cpp engine is where this "
                      'model works.',
              'issues': []},
 'omlx': {'status': 'degraded',
          'label': 'Runs, degraded',
          'note': 'oMLX explicitly ships native kernels for MiniMax M3, so it is the MLX '
                  'engine that intends to run this. In practice the checkpoint is '
                  '`minimax_m3_vl` and loading has failed with 2225 vision-tower parameters '
                  'rejected rather than skipped, alongside a model-type mapping error and an '
                  'open question about which quant tiers the long-prefill fixes actually '
                  'cover. Promising, not yet dependable.',
          'issues': ['jundot/omlx#1968', 'jundot/omlx#1862', 'jundot/omlx#2590']},
 'vllmmlx': {'status': 'blocked',
             'label': 'Blocked',
             'note': 'There is no MiniMax M3 text backbone in mlx-lm - PR #1401 is still open '
                     '- so there is nothing for vllm-mlx to wrap.',
             'issues': ['ml-explore/mlx-lm#1401']},
 'mlxlm': {'status': 'blocked',
           'label': 'Blocked',
           'note': '`minimax.py` covers the earlier MiniMax generation, not M3. The M3 text '
                   'backbone is PR #1401, unmerged. The mlx-community 4-bit was produced with '
                   'mlx-vlm, which is a different package and a different code path.',
           'issues': ['ml-explore/mlx-lm#1401']},
 'vllmmetal': {'status': 'blocked',
               'label': 'Blocked',
               'note': "Not in the support matrix, and MiniMax M3's sparse attention would "
                       'need its own kernel work.',
               'issues': []},
 'ds4': {'status': 'none',
         'label': 'Out of scope',
         'note': 'Not one of the three checkpoints ds4 loads.',
         'issues': []},
 'mtplx': {'status': 'blocked',
           'label': 'Unsupported architecture',
           'note': 'The catalog carries a MiniMax entry, but it is `minimax_m2` and it is in '
                   'the `recognized-backend-pending` tier with no backend behind it. '
                   '`minimax_m3` does not match it, so there is nothing to fall back to. This '
                   'is not the vision-tower problem that stops oMLX - MTPLX never gets as far '
                   'as loading tensors.',
           'issues': []}}
