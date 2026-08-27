"""Qwen3.8-Flash-Next - model record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'q38fnext'
MODALITY = 'text'
NAME = 'Qwen3.8-Flash-Next'
ARCH = 'MoE 125B + 51B n-gram embedding / 6B active · Gated DeltaNet + Qwen Sparse Attention'
LICENSE = 'Qwen Community 1.0'
CONTEXT = '262k (1M on the hosted version)'
HF = 'Qwen/Qwen3.8-Flash-Next'
PARAMS_B = 180

NOTE = ('Qwen calls this an experimental preview of the architecture behind Qwen4, and the numbers '
 'are the strongest per active parameter on this page: 6B active beats Qwen3.8-27B on every '
 'shared benchmark, and its SWE-bench Multilingual of 81.0 leads the page outright. Three '
 'genuinely new pieces - Qwen Sparse Attention at micro-block granularity, gated residuals, '
 'and a 51B n-gram embedding table designed to be offloaded. That last one is why the '
 'checkpoint is 180B on disk against a stated 125B. None of it runs on Apple silicon yet: the '
 'architecture is `qwen4_exp` and no runtime here implements it.')

SOURCES = [('Model card with full tables', 'https://huggingface.co/Qwen/Qwen3.8-Flash-Next'),
 ('Qwen blog', 'https://qwen.ai/blog?id=qwen3.8-flash-next')]

SCORES = {'agentic': [('Toolathlon Verified', '73.5'),
             ('CoWorkBench', '73.9'),
             ('JobBench', '55.7'),
             ('Agents’ Last Exam', '24.3')],
 'coding': [('SWE-bench Multilingual', '81.0'),
            ('SWE-bench Pro', '62.5'),
            ('LiveCodeBench v6', '91.9'),
            ('DeepSWE 1.1', '58.7')]}

# Which engine the card opens on and the glance row names.
BEST_ENGINE = 'llamacpp'

# Repositories tracker/measure.py harvests for this model.
QUANT_SOURCES = {'gguf': ['unsloth/Qwen3.8-Flash-Next-GGUF']}

# Measured by tracker/measure.py - do not hand-edit. gb is summed repo bytes;
# bpw is gb*8/PARAMS_B and is omitted for pruned or native-precision builds.
LADDER = {'gguf': [{'bpw': 4.95,
           'gb': 111.3,
           'kind': 'quant',
           'label': 'Qwen3.8-Flash-Next-UD-Q4_K_XL',
           'repo': 'unsloth/Qwen3.8-Flash-Next-GGUF'},
          {'bpw': 4.16,
           'gb': 93.7,
           'kind': 'quant',
           'label': 'Qwen3.8-Flash-Next-UD-IQ4_XS',
           'repo': 'unsloth/Qwen3.8-Flash-Next-GGUF'},
          {'bpw': 4.0,
           'gb': 90.0,
           'kind': 'quant',
           'label': 'Qwen3.8-Flash-Next-UD-Q3_K_XL',
           'repo': 'unsloth/Qwen3.8-Flash-Next-GGUF'},
          {'bpw': 3.64,
           'gb': 82.0,
           'kind': 'quant',
           'label': 'Qwen3.8-Flash-Next-UD-IQ3_XXS',
           'repo': 'unsloth/Qwen3.8-Flash-Next-GGUF'},
          {'bpw': 3.51,
           'gb': 78.9,
           'kind': 'quant',
           'label': 'Qwen3.8-Flash-Next-UD-Q2_K_XL',
           'repo': 'unsloth/Qwen3.8-Flash-Next-GGUF'},
          {'bpw': 3.31,
           'gb': 74.5,
           'kind': 'quant',
           'label': 'Qwen3.8-Flash-Next-UD-IQ1_M',
           'repo': 'unsloth/Qwen3.8-Flash-Next-GGUF'}],
 'mlx': []}

# Bytes of KV per token at fp16, the context ceiling, and how it was derived.
# None for models with no growing cache (diffusion, TTS).
KV = {'bytes_per_token': 24576,
 'max_context': 262144,
 'derivation': '12 of 48 layers use Qwen Sparse Attention at micro-block granularity with a '
               '2048 budget, so this is an upper bound; the other 36 are Gated DeltaNet'}

# Per-engine status. Keys must be engines whose modality matches MODALITY.
ENGINES = {'llamacpp': {'status': 'blocked',
              'label': 'Blocked',
              'note': 'This is a preview of the Qwen4 architecture, not a Qwen3 variant: the '
                      "config reports `qwen4_exp`, and llama.cpp's architecture table has "
                      '`qwen3next` but nothing for qwen4. Support is an open feature request. '
                      'One GGUF has been published - a single UD-IQ1_S tier at 72.5 GB - but '
                      'mainline has no loader for it, so the file exists ahead of the runtime.',
              'issues': ['ggml-org/llama.cpp#27741']},
 'ollama': {'status': 'blocked',
            'label': 'Blocked',
            'note': 'Not in the library, and it inherits the same missing architecture '
                    'underneath.',
            'issues': []},
 'lmstudio': {'status': 'blocked',
              'label': 'Blocked',
              'note': 'Nothing curated in either format. Both of its engines are downstream of '
                      'the two projects that do not implement this architecture yet.',
              'issues': []},
 'omlx': {'status': 'blocked',
          'label': 'Blocked',
          'note': 'No MLX conversion exists and mlx-lm has no qwen4 model class, so there is '
                  'nothing to load. oMLX does ship native Qwen3.5 kernels, which is a '
                  'reasonable signal that it would pick this up once upstream does.',
          'issues': []},
 'vllmmlx': {'status': 'blocked',
             'label': 'Blocked',
             'note': 'Wraps mlx-lm, which has no qwen4 class. Nothing to wrap.',
             'issues': []},
 'mlxlm': {'status': 'blocked',
           'label': 'Blocked',
           'note': 'The models directory carries qwen3_next but nothing for qwen4. This is the '
                   'upstream gap every MLX engine on this page inherits.',
           'issues': []},
 'vllmmetal': {'status': 'blocked',
               'label': 'Blocked',
               'note': 'The matrix covers Qwen3.5 through 3.8, not the qwen4_exp preview '
                       'architecture. Same upstream gap every MLX engine here has.',
               'issues': []},
 'ds4': {'status': 'none',
         'label': 'Out of scope',
         'note': 'Not one of the three checkpoints ds4 loads.',
         'issues': []}}
