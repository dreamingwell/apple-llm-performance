"""DeepSeek V4 Pro - model record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'v4pro'
MODALITY = 'text'
NAME = 'DeepSeek V4 Pro'
ARCH = 'MoE 1.6T total / 49B active · DSA sparse attention'
LICENSE = 'MIT'
CONTEXT = '1M'
HF = 'deepseek-ai/DeepSeek-V4-Pro-0813'
PARAMS_B = 1600

NOTE = ('Same architecture as Flash at roughly five times the size, which makes it a capacity problem '
 'rather than a compatibility one. It runs, on hardware most people will not have: a 512 GB '
 'machine, or a pair of them for the Q4 split. Worth knowing it exists so you can price the '
 'ceiling.')

SOURCES = [('Artificial Analysis writeup',
  'https://artificialanalysis.ai/articles/deepseek-is-back-among-the-leading-open-weights-models-with-v4-pro-and-v4-flash')]

SCORES = {'agentic': [('GDPval-AA', '1554')], 'coding': [('SWE-bench Verified', '80.6%')]}

# Which engine the card opens on and the glance row names.
BEST_ENGINE = 'ds4'

# Repositories tracker/measure.py harvests for this model.
QUANT_SOURCES = {'ds4': ['antirez/deepseek-v4-gguf'],
 'gguf': ['unsloth/DeepSeek-V4-Pro-0813-GGUF'],
 'mlx': ['mlx-community/DeepSeek-V4-Pro-4bit',
         'inferencerlabs/DeepSeek-V4-Pro-Preview-MLX-Q2.8-INF']}

# Measured by tracker/measure.py - do not hand-edit. gb is summed repo bytes;
# bpw is gb*8/PARAMS_B and is omitted for pruned or native-precision builds.
# Some quant repos hold more than one checkpoint; a family listed here is
# filtered to files matching this pattern.
QUANT_FILTER = {'ds4': 'V4-Pro'}

LADDER = {'ds4': [{'bpw': 2.32,
          'gb': 464.6,
          'kind': 'quant',
          'label': 'DeepSeek-V4-Pro-IQ2XXS-w2Q2K-AProjQ8-SExpQ8-OutQ8-Instruct',
          'repo': 'antirez/deepseek-v4-gguf'},
         {'bpw': 2.21,
          'gb': 442.0,
          'kind': 'quant',
          'label': 'DeepSeek-V4-Pro-Q4K-Layers-31-output',
          'repo': 'antirez/deepseek-v4-gguf'}],
 'gguf': [{'bpw': 4.37,
           'gb': 873.4,
           'kind': 'quant',
           'label': 'DeepSeek-V4-Pro-0813-UD-Q8_K_XL',
           'repo': 'unsloth/DeepSeek-V4-Pro-0813-GGUF'}],
 'mlx': [{'bpw': 4.19,
          'gb': 837.01,
          'kind': 'quant',
          'label': 'DeepSeek-V4-Pro-4bit',
          'repo': 'mlx-community/DeepSeek-V4-Pro-4bit'},
         {'bpw': 2.81,
          'gb': 562.2,
          'kind': 'quant',
          'label': 'DeepSeek-V4-Pro-Preview-MLX-Q2.8-INF',
          'repo': 'inferencerlabs/DeepSeek-V4-Pro-Preview-MLX-Q2.8-INF'}]}

# Bytes of KV per token at fp16, the context ceiling, and how it was derived.
# None for models with no growing cache (diffusion, TTS).
KV = {'bytes_per_token': 70272,
 'max_context': 1048576,
 'derivation': '61 layers of DSA latent attention, 512 + 64 rope'}

# Per-engine status. Keys must be engines whose modality matches MODALITY.
ENGINES = {'vllmmetal': {'status': 'blocked',
               'label': 'Blocked',
               'note': 'Same as Flash - the architecture is not in the matrix, and MLA has no '
                       'Metal kernel yet.',
               'issues': ['vllm-project/vllm-metal#360']},
 'ds4': {'status': 'works',
         'label': 'Best path',
         'note': 'ds4 runs PRO, with the honest caveat that it takes real hardware. The '
                 'IQ2_XXS routed build is 464.6 GB in one file - a 512 GB machine, or pooled '
                 'across two 256 GB machines by pipeline parallelism. The Q4 split ships as '
                 'two files of 457.5 GB and 442.0 GB, designed for a pair of 512 GB Mac '
                 'Studios with the coordinator taking layers 0-30 and the worker taking 31 to '
                 'output. Measured: 9.56 tok/s generation on PRO q2 at 32k context on a 512 GB '
                 'M3 Ultra. Note the 0813 refresh is not yet a supported checkpoint.',
         'issues': ['antirez/ds4#807',
                    'antirez/ds4#845',
                    'antirez/ds4#853',
                    'antirez/ds4#816',
                    'antirez/ds4#805']},
 'llamacpp': {'status': 'works',
              'label': 'Runs',
              'note': 'Same `deepseek4` path as Flash, so it loads - and inherits the same '
                      'agent-shaped defects, on a model large enough that you will not be '
                      'iterating quickly while you hit them.',
              'issues': ['ggml-org/llama.cpp#26965',
                         'ggml-org/llama.cpp#25171',
                         'ggml-org/llama.cpp#25796']},
 'ollama': {'status': 'works',
            'label': 'Runs',
            'note': 'In the library. Fit is the constraint, not availability.',
            'issues': []},
 'lmstudio': {'status': 'works',
              'label': 'Runs',
              'note': 'GGUF engine only - there is no MLX model class for this architecture.',
              'issues': []},
 'omlx': {'status': 'blocked',
          'label': 'Blocked',
          'note': "oMLX's DeepSeek V4 path exists, but nobody has published a PRO conversion. "
                   'The residency problem filed against Flash has since been fixed, but the '
                   'MXFP4 float32 crash is still open and would apply here at four times the '
                   'size.',
          'issues': ['jundot/omlx#2469']},
 'vllmmlx': {'status': 'blocked',
             'label': 'Blocked',
             'note': 'Same wall as Flash: no deepseek_v4 in mlx-lm to wrap, and no PRO quant '
                     'if there were.',
             'issues': ['waybarrios/vllm-mlx#668', 'ml-explore/mlx-lm#1233']},
 'mlxlm': {'status': 'blocked',
           'label': 'Blocked',
           'note': 'No model class, no published conversion.',
           'issues': ['ml-explore/mlx-lm#1233', 'ml-explore/mlx-lm#1443']}}
