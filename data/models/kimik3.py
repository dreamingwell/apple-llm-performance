"""Kimi K3 - model record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'kimik3'
MODALITY = 'text'
NAME = 'Kimi K3'
ARCH = 'MoE 2.8T total / 104B active'
LICENSE = 'Modified MIT'
CONTEXT = '1M'
HF = 'moonshotai/Kimi-K3'
PARAMS_B = 2780

NOTE = ('The best open-weight agentic model there is - Terminal-Bench 2.1 of 88.3, MCPMark-Verified '
 '94.5 - and the hardest to get onto a Mac. Both available routes trade quality for fit: 1-bit '
 'GGUF tiers on one side, community expert-pruned MLX builds on the other. Neither is the '
 'model the benchmarks describe, and the honest position is that nobody has published '
 'Apple-hardware evaluations of either.')

SOURCES = [('Benchmark roundup', 'https://www.morphllm.com/best-open-source-llm')]

SCORES = {'agentic': [('Terminal-Bench 2.1', '88.3'),
             ('MCPMark-Verified', '94.5'),
             ('OSWorld-Verified', '84.8')],
 'coding': [('LiveBench Coding', '81.45'), ('Agentic Coding', '57.58')]}

# Which engine the card opens on and the glance row names.
BEST_ENGINE = 'llamacpp'

# Repositories tracker/measure.py harvests for this model.
QUANT_SOURCES = {'gguf': ['unsloth/Kimi-K3-GGUF'],
 'mlx': ['pipenetwork/Kimi-K3-REAP73-MLX-mxfp4-q8', 'pipenetwork/Kimi-K3-REAP80-MLX-mxfp4-q8']}

# Measured by tracker/measure.py - do not hand-edit. gb is summed repo bytes;
# bpw is gb*8/PARAMS_B and is omitted for pruned or native-precision builds.
LADDER = {'gguf': [{'bpw': 4.49,
           'gb': 1561.2,
           'kind': 'quant',
           'label': 'Kimi-K3-UD-Q8_K_XL',
           'repo': 'unsloth/Kimi-K3-GGUF'},
          {'bpw': 4.34,
           'gb': 1508.7,
           'kind': 'quant',
           'label': 'Kimi-K3-UD-Q4_K_XL',
           'repo': 'unsloth/Kimi-K3-GGUF'},
          {'bpw': 2.48,
           'gb': 861.3,
           'kind': 'quant',
           'label': 'Kimi-K3-UD-Q2_K_XL',
           'repo': 'unsloth/Kimi-K3-GGUF'},
          {'bpw': 2.05,
           'gb': 711.1,
           'kind': 'quant',
           'label': 'Kimi-K3-UD-IQ2_XXS',
           'repo': 'unsloth/Kimi-K3-GGUF'},
          {'bpw': 1.87,
           'gb': 648.9,
           'kind': 'quant',
           'label': 'Kimi-K3-UD-IQ1_M',
           'repo': 'unsloth/Kimi-K3-GGUF'},
          {'bpw': 1.71,
           'gb': 594.0,
           'kind': 'quant',
           'label': 'Kimi-K3-UD-IQ1_S',
           'repo': 'unsloth/Kimi-K3-GGUF'},
          {'bpw': 1.59,
           'gb': 551.5,
           'kind': 'quant',
           'label': 'Kimi-K3-UD-TQ2_0',
           'repo': 'unsloth/Kimi-K3-GGUF'},
          {'bpw': 1.46,
           'gb': 508.9,
           'kind': 'quant',
           'label': 'Kimi-K3-UD-TQ1_0',
           'repo': 'unsloth/Kimi-K3-GGUF'},
          {'bpw': 1.34,
           'gb': 466.4,
           'kind': 'quant',
           'label': 'Kimi-K3-UD-Q1_0',
           'repo': 'unsloth/Kimi-K3-GGUF'}],
 'mlx': [{'bpw': None,
          'gb': 451.42,
          'kind': 'pruned',
          'label': 'Kimi-K3-REAP73-MLX-mxfp4-q8',
          'repo': 'pipenetwork/Kimi-K3-REAP73-MLX-mxfp4-q8'},
         {'bpw': None,
          'gb': 349.67,
          'kind': 'pruned',
          'label': 'Kimi-K3-REAP80-MLX-mxfp4-q8',
          'repo': 'pipenetwork/Kimi-K3-REAP80-MLX-mxfp4-q8'}]}

# Bytes of KV per token at fp16, the context ceiling, and how it was derived.
# None for models with no growing cache (diffusion, TTS).
KV = {'bytes_per_token': 27648,
 'max_context': 1048576,
 'derivation': '24 of 93 layers are full attention; the other 69 hold a fixed KDA state'}

# Per-engine status. Keys must be engines whose modality matches MODALITY.
ENGINES = {'llamacpp': {'status': 'works',
              'label': 'Runs',
              'note': '`kimi-k3` is in mainline, which makes the best open-weight agentic '
                      'model on this page reachable on Apple hardware at all. Reachable, not '
                      'comfortable: the smallest build is UD-Q1_0 at 466.4 GB, TQ1_0 is 508.9 '
                      'GB, and Q2_K_XL is 861 GB. At 1-bit the question is no longer whether '
                      'it loads but whether it is still the model whose Terminal-Bench 2.1 is '
                      '88.3. Vision is on a branch; the text backbone is not.',
              'issues': ['ggml-org/llama.cpp#26365']},
 'ollama': {'status': 'works',
            'label': 'Runs',
            'note': 'In the library. The tag you can actually run is decided by your pooled '
                    'memory, not by preference.',
            'issues': []},
 'lmstudio': {'status': 'works',
              'label': 'Runs',
              'note': 'GGUF engine. mlx-lm has no kimi_k3 class, so its MLX engine is not an '
                      'option.',
              'issues': []},
 'omlx': {'status': 'degraded',
          'label': 'Community builds only',
          'note': 'There is an MLX route, and it is a compromise rather than a port. Community '
                  'REAP builds prune routed experts - keeping 179 of 896 per layer - to get '
                  'from 1.56 TB down to 350 GB, and the publisher measures 5.54 tok/s on a 512 '
                  'GB M3 Ultra while documenting the degradation candidly, including Chinese '
                  'output looping in that build. Note that pruning buys memory, not speed: '
                  'per-token traffic depends on top-k and non-expert precision, so a 350 GB '
                  'and a 451 GB build decode at the same rate. mlx-lm has no kimi_k3 model '
                  'class, so these repos ship their own modelling code.',
          'issues': []},
 'vllmmlx': {'status': 'degraded',
             'label': 'Pruned builds only',
             'note': 'Wraps mlx-lm, which gained a `kimi_k3` class on 2026-09-01, so there is '
                      'now an architecture to wrap. The practical limit is the same one '
                      'everywhere on this model: the only MLX builds published are expert- '
                      'pruned.',
             'issues': []},
 'mlxlm': {'status': 'degraded',
           'label': 'Pruned builds only',
           'note': 'mlx-lm merged a `kimi_k3` model class on 2026-09-01, so the architecture '
                    'gap that used to block this is closed - the community REAP repos that '
                    'shipped their own modelling code via `auto_map` are no longer the only '
                    'route. What has not changed is the size: no unpruned MLX conversion exists, '
                    'so in practice you are still loading a REAP build with most of its routed '
                    'experts deleted. Treat this as loadable rather than solved.',
           'issues': ['ml-explore/mlx-lm#1572']},
 'vllmmetal': {'status': 'blocked',
               'label': 'Blocked',
               'note': 'The support matrix has not been updated for K3, though mlx-lm now '
                        'carries the class it would build on. Still no unpruned MLX build to try '
                        'even if it had.',
               'issues': []},
 'ds4': {'status': 'none',
         'label': 'Out of scope',
         'note': 'Not one of the three checkpoints ds4 loads.',
         'issues': []}}
