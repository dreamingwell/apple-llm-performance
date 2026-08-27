"""Nemotron 3.5 Lightning - model record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'nemolight'
MODALITY = 'text'
NAME = 'Nemotron 3.5 Lightning'
ARCH = 'MoE 30B total / ~3B active · hybrid Mamba-Transformer'
LICENSE = 'NVIDIA OpenMDW-1.1'
CONTEXT = '128k'
HF = 'nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B'
PARAMS_B = 30

NOTE = ('Released 2026-08-11 with weights, training data and recipes. 3B active makes it the cheapest '
 'thing here to run at concurrency, and the checkpoint ships MTP draft weights. Published '
 'agentic coverage is thin - NVIDIA leads with general benchmarks - so treat it as a fast tier '
 'to trial rather than a proven agentic pick. The larger Nemotron 3 Super (120B-A12B) and '
 'Ultra (550B-A55B, SWE-bench Verified 70.7) are stronger but have no Apple-ready quantisation '
 'published.')

SOURCES = [('NVIDIA model card',
  'https://build.nvidia.com/nvidia/nemotron-3.5-lightning-30b-a3b/modelcard'),
 ('Benchmark writeup', 'https://www.datacamp.com/blog/nemotron-3-5-lightning')]

SCORES = {'agentic': [('MMLU Pro', '81.94'), ('GPQA Diamond', '75.44')],
 'coding': [('SWE-bench Verified', '51.56'), ('PinchBench', '85.37')]}

# Which engine the card opens on and the glance row names.
BEST_ENGINE = 'ollama'

# Repositories tracker/measure.py harvests for this model.
QUANT_SOURCES = {'gguf': ['unsloth/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-GGUF',
          'ggml-org/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-GGUF'],
 'mlx': ['mlx-community/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-8bit',
         'mlx-community/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-4bit',
         'mlx-community/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-mxfp4']}

# Measured by tracker/measure.py - do not hand-edit. gb is summed repo bytes;
# bpw is gb*8/PARAMS_B and is omitted for pruned or native-precision builds.
LADDER = {'gguf': [{'bpw': 17.56,
           'gb': 65.9,
           'kind': 'quant',
           'label': 'NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16',
           'repo': 'unsloth/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-GGUF'},
          {'bpw': 10.3,
           'gb': 38.6,
           'kind': 'quant',
           'label': 'NVIDIA-Nemotron-3.5-Lightning-30B-A3B-UD-Q8_K_XL',
           'repo': 'unsloth/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-GGUF'},
          {'bpw': 9.33,
           'gb': 35.0,
           'kind': 'quant',
           'label': 'NVIDIA-Nemotron-3.5-Lightning-30B-A3B-Q8_0',
           'repo': 'unsloth/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-GGUF'},
          {'bpw': 8.96,
           'gb': 33.6,
           'kind': 'quant',
           'label': 'NVIDIA-Nemotron-3.5-Lightning-30B-A3B-Q8_0',
           'repo': 'ggml-org/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-GGUF'},
          {'bpw': 6.99,
           'gb': 26.2,
           'kind': 'quant',
           'label': 'NVIDIA-Nemotron-3.5-Lightning-30B-A3B-UD-Q5_K_S',
           'repo': 'unsloth/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-GGUF'},
          {'bpw': 6.52,
           'gb': 24.5,
           'kind': 'quant',
           'label': 'NVIDIA-Nemotron-3.5-Lightning-30B-A3B-UD-Q4_K_S',
           'repo': 'unsloth/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-GGUF'},
          {'bpw': 6.19,
           'gb': 23.2,
           'kind': 'quant',
           'label': 'NVIDIA-Nemotron-3.5-Lightning-30B-A3B-MXFP4_MOE',
           'repo': 'unsloth/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-GGUF'},
          {'bpw': 5.64,
           'gb': 21.2,
           'kind': 'quant',
           'label': 'NVIDIA-Nemotron-3.5-Lightning-30B-A3B-UD-IQ3_S',
           'repo': 'unsloth/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-GGUF'},
          {'bpw': 5.04,
           'gb': 18.9,
           'kind': 'quant',
           'label': 'NVIDIA-Nemotron-3.5-Lightning-30B-A3B-Q4_0',
           'repo': 'ggml-org/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-GGUF'}],
 'mlx': [{'bpw': 8.95,
          'gb': 33.56,
          'kind': 'quant',
          'label': 'NVIDIA-Nemotron-3.5-Lightning-30B-A3B-8bit',
          'repo': 'mlx-community/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-8bit'},
         {'bpw': 4.74,
          'gb': 17.78,
          'kind': 'quant',
          'label': 'NVIDIA-Nemotron-3.5-Lightning-30B-A3B-4bit',
          'repo': 'mlx-community/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-4bit'},
         {'bpw': 4.48,
          'gb': 16.79,
          'kind': 'quant',
          'label': 'NVIDIA-Nemotron-3.5-Lightning-30B-A3B-mxfp4',
          'repo': 'mlx-community/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-mxfp4'}]}

# Bytes of KV per token at fp16, the context ceiling, and how it was derived.
# None for models with no growing cache (diffusion, TTS).
KV = {'bytes_per_token': 6144,
 'max_context': 262144,
 'derivation': 'hybrid Mamba-Transformer: only the handful of attention layers grow, the SSM '
               'state is fixed'}

# Per-engine status. Keys must be engines whose modality matches MODALITY.
ENGINES = {'llamacpp': {'status': 'degraded',
              'label': 'Runs, degraded',
              'note': 'ggml-org publishes it, with separate MTP draft weights at Q4/Q8/BF16 so '
                      'speculative decoding is available. The catch is `nemotron_h_moe` '
                      'aborting inside ggml_ssm_scan during context reservation - before '
                      'generation starts, in the shared SSM kernel rather than a '
                      'backend-specific path. Check that issue against your build before '
                      'committing to this one.',
              'issues': ['ggml-org/llama.cpp#27141']},
 'ollama': {'status': 'works',
            'label': 'Runs',
            'note': 'In the library. The simplest route to trying the model, and at 3B active '
                    'it is cheap to leave running.',
            'issues': []},
 'lmstudio': {'status': 'works',
              'label': 'Runs',
              'note': 'Curated GGUF plus the mlx-community 4-bit. Given the llama.cpp SSM '
                      'assertion above, having the MLX path a click away is the practical '
                      'value here.',
              'issues': []},
 'omlx': {'status': 'works',
          'label': 'Runs',
          'note': 'Loads on the nemotron_h path with nothing architecture-level open against '
                  'it. MTP is not wired up yet, so the draft weights NVIDIA shipped go unused '
                  '- speed left on the table rather than a defect.',
          'issues': ['jundot/omlx#1195']},
 'vllmmlx': {'status': 'works',
             'label': 'Runs',
             'note': '3B active makes this the cheapest thing here to run at concurrency, and '
                     'nothing for this architecture is open in mlx-lm.',
             'issues': []},
 'mlxlm': {'status': 'works',
           'label': 'Runs',
           'note': 'Runs on the hybrid Mamba-Transformer path without special handling.',
           'issues': []},
 'vllmmetal': {'status': 'blocked',
               'label': 'Blocked',
               'note': 'Nemotron-H paged attention is an open request - the Mamba-2 plus MoE '
                       'hybrid has no implementation here yet. That issue is the thing to '
                       'watch.',
               'issues': ['vllm-project/vllm-metal#644']},
 'ds4': {'status': 'none',
         'label': 'Out of scope',
         'note': 'Not one of the three checkpoints ds4 loads.',
         'issues': []}}
