"""Qwen3.8-27B - model record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'qwen38'
MODALITY = 'text'
NAME = 'Qwen3.8-27B'
ARCH = 'Dense 27.8B · hybrid GDN (48 linear + 16 full-attn)'
LICENSE = 'Apache-2.0'
CONTEXT = '262k (to 1M)'
HF = 'Qwen/Qwen3.8-27B'
PARAMS_B = 27.8

NOTE = ("Stronger on paper than its size suggests: SWE-bench Pro of 61.7 is within noise of "
 "GLM-5.2's 62.1 at 1/27th the scale, and LiveCodeBench-v6 of 90.3 is the highest here. Its hybrid "
 'Gated DeltaNet layout is also the most engine-sensitive thing here - the same weights get '
 'working multi-token speculative decoding on one engine and a k=1 cap on another, so which '
 'runtime you pick changes the throughput more than which quant you pick.')

SOURCES = [('Model card (all scores)', 'https://huggingface.co/Qwen/Qwen3.8-27B')]

SCORES = {'agentic': [('Terminal-Bench 2.1', '73.0'),
             ('OSWorld (computer use)', '84.3'),
             ('AndroidWorld', '81.9'),
             ('WebArena', '64.8')],
 'coding': [('LiveCodeBench-v6', '90.3'),
            ('QwenSWEBench', '79.0'),
            ('SWE-bench Pro', '61.7'),
            ('DeepSWE 1.1', '42.2')]}

# Which engine the card opens on and the glance row names.
BEST_ENGINE = 'llamacpp'

# Repositories tracker/measure.py harvests for this model.
QUANT_SOURCES = {'gguf': ['unsloth/Qwen3.8-27B-GGUF'],
 'mlx': ['mlx-community/Qwen3.8-27B-8bit',
         'lmstudio-community/Qwen3.8-27B-MLX-6bit',
         'mlx-community/Qwen3.8-27B-OptiQ-4bit',
         'lmstudio-community/Qwen3.8-27B-MLX-5bit',
         'mlx-community/Qwen3.8-27B-4bit']}

# Measured by tracker/measure.py - do not hand-edit. gb is summed repo bytes;
# bpw is gb*8/PARAMS_B and is omitted for pruned or native-precision builds.
LADDER = {'gguf': [{'label': 'Qwen3.8-27B-BF16',
           'repo': 'unsloth/Qwen3.8-27B-GGUF',
           'gb': 54.66,
           'kind': 'quant',
           'bpw': 15.73},
          {'label': 'Qwen3.8-27B-UD-Q8_K_L',
           'repo': 'unsloth/Qwen3.8-27B-GGUF',
           'gb': 28.05,
           'kind': 'quant',
           'bpw': 8.07},
          {'label': 'Qwen3.8-27B-UD-Q6_K_M',
           'repo': 'unsloth/Qwen3.8-27B-GGUF',
           'gb': 23.09,
           'kind': 'quant',
           'bpw': 6.64},
          {'label': 'Qwen3.8-27B-UD-Q5_K_XL',
           'repo': 'unsloth/Qwen3.8-27B-GGUF',
           'gb': 20.88,
           'kind': 'quant',
           'bpw': 6.01},
          {'label': 'Qwen3.8-27B-UD-Q4_K_XL',
           'repo': 'unsloth/Qwen3.8-27B-GGUF',
           'gb': 17.56,
           'kind': 'quant',
           'bpw': 5.05},
          {'label': 'Qwen3.8-27B-UD-IQ4_XS',
           'repo': 'unsloth/Qwen3.8-27B-GGUF',
           'gb': 14.25,
           'kind': 'quant',
           'bpw': 4.1},
          {'label': 'Qwen3.8-27B-UD-IQ3_S',
           'repo': 'unsloth/Qwen3.8-27B-GGUF',
           'gb': 12.04,
           'kind': 'quant',
           'bpw': 3.47},
          {'label': 'Qwen3.8-27B-UD-IQ2_S',
           'repo': 'unsloth/Qwen3.8-27B-GGUF',
           'gb': 8.37,
           'kind': 'quant',
           'bpw': 2.41},
          {'label': 'Qwen3.8-27B-UD-IQ1_S',
           'repo': 'unsloth/Qwen3.8-27B-GGUF',
           'gb': 6.19,
           'kind': 'quant',
           'bpw': 1.78}],
 'mlx': [{'label': 'Qwen3.8-27B-8bit',
          'repo': 'mlx-community/Qwen3.8-27B-8bit',
          'gb': 29.5,
          'kind': 'quant',
          'bpw': 8.49},
         {'label': 'Qwen3.8-27B-MLX-6bit',
          'repo': 'lmstudio-community/Qwen3.8-27B-MLX-6bit',
          'gb': 22.78,
          'kind': 'quant',
          'bpw': 6.55},
         {'label': 'Qwen3.8-27B-OptiQ-4bit',
          'repo': 'mlx-community/Qwen3.8-27B-OptiQ-4bit',
          'gb': 20.66,
          'kind': 'quant',
          'bpw': 5.95},
         {'label': 'Qwen3.8-27B-MLX-5bit',
          'repo': 'lmstudio-community/Qwen3.8-27B-MLX-5bit',
          'gb': 19.42,
          'kind': 'quant',
          'bpw': 5.59},
         {'label': 'Qwen3.8-27B-4bit',
          'repo': 'mlx-community/Qwen3.8-27B-4bit',
          'gb': 16.05,
          'kind': 'quant',
          'bpw': 4.62}]}

# Bytes of KV per token at fp16, the context ceiling, and how it was derived.
# None for models with no growing cache (diffusion, TTS).
KV = {'bytes_per_token': 65536,
 'max_context': 262144,
 'derivation': '16 of 64 layers are full attention, one in every 4; the other 48 are linear'}

# Per-engine status. Keys must be engines whose modality matches MODALITY.
ENGINES = {'llamacpp': {'status': 'works',
              'label': 'Runs',
              'note': 'The better path for this model, for one specific reason: the GGUF repo '
                      'ships a separate 1.4 GB MTP draft head, so `--draft-mtp` gives you real '
                      'multi-token speculative decoding - exactly the thing that is capped at '
                      'k=1 on the MLX servers. A 29-tier quant ladder from 6.2 GB to 31.5 GB '
                      'on top. Watch two Mac-specific things: a crash on an M2 Ultra with '
                      'default settings, and a chat template that mis-renders tool calls until '
                      'you substitute the Qwen3.6 one.',
              'issues': ['ggml-org/llama.cpp#27335',
                         'ggml-org/llama.cpp#27139',
                         'ggml-org/llama.cpp#27428']},
 'ollama': {'status': 'works',
            'label': 'Runs',
            'note': 'In the library with 18/30/32/56 GB tags. Since Ollama now defaults to MLX '
                    'on Apple Silicon, whether you get the MTP speedup depends on which path '
                    'your tag resolves to - benchmark it rather than assuming.',
            'issues': ['ollama/ollama#17776']},
 'lmstudio': {'status': 'works',
              'label': 'Runs',
              'note': 'Curated in both formats, which makes it the cheapest way to settle the '
                      'question this model raises: the MLX build decodes faster per token in '
                      'principle, the GGUF build gets working MTP. Run both.',
              'issues': []},
 'omlx': {'status': 'degraded',
          'label': 'Runs, degraded',
          'note': 'oMLX ships native Metal kernels for the Qwen3.5 family, which is the right '
                  'answer to this hybrid GDN architecture, and it is the strongest MLX option '
                  'for the model. It is still degraded rather than clean: single-stream decode '
                  'has regressed from about 36.5 to 24 tok/s on an M3 Ultra with the MTP path '
                  'implicated, continuous batching on this architecture is unmeasured, and '
                  'loading a second Qwen-family model can contaminate a resident engine.',
          'issues': ['jundot/omlx#2747',
                     'jundot/omlx#2854',
                     'jundot/omlx#2972',
                     'jundot/omlx#3117',
                     'jundot/omlx#2691']},
 'vllmmlx': {'status': 'degraded',
             'label': 'Runs, degraded',
             'note': 'What holds this model back here is the runtime, not the model. Prefix '
                     'caching is off on hybrid linear-attention architectures and speculative '
                     'decoding is capped at k=1, so you pay full re-prefill on every turn and '
                     'get none of the MTP head the checkpoint carries. The published '
                     'Terminal-Bench 2.1 of 73.0 is the best agentic number among things that '
                     'run - it is just not what you measure on this engine.',
             'issues': ['waybarrios/vllm-mlx#730',
                        'waybarrios/vllm-mlx#731',
                        'waybarrios/vllm-mlx#710',
                        'ml-explore/mlx-lm#1446',
                        'waybarrios/vllm-mlx#678',
                        'waybarrios/vllm-mlx#641',
                        'waybarrios/vllm-mlx#711',
                        'waybarrios/vllm-mlx#729',
                        'waybarrios/vllm-mlx#689',
                        'waybarrios/vllm-mlx#658',
                        'waybarrios/vllm-mlx#699']},
 'mlxlm': {'status': 'works',
           'label': 'Runs',
           'note': 'The qwen3_5 class works for single-stream generation. The cache '
                   'limitations that make this architecture painful on the servers above start '
                   'here: ArraysCache is not trimmable, which is the cause of the k=1 '
                   'speculative-decoding cap downstream.',
           'issues': ['ml-explore/mlx-lm#1446', 'ml-explore/mlx-lm#1335']},
 'vllmmetal': {'status': 'works',
               'label': 'Runs',
               'note': 'The strongest MLX-backed option for this model, and worth being '
                       "precise about why, because the name suggests otherwise: this is vLLM's "
                       'scheduler and API over MLX as the compute layer. It pins `mlx==0.32.0` '
                       'exactly, depends on mlx-lm and mlx-vlm, and its paged attention kernel '
                       'is implemented as an `mlx::core::Primitive` subclass rather than '
                       'running beside MLX. What it adds on top is hardware-specific: as of '
                       'August 2026 it uses the M5 Neural Accelerator tensor units for MHA, '
                       'GQA and MQA prefill, which no other engine here claims. '
                       "`mlx-community/Qwen3.8-27B-8bit` is the project's own example "
                       'checkpoint for the hybrid SDPA + GDN path, so this is the '
                       'configuration they test. Prefix caching works but is opt-in on hybrid '
                       'GDN - pass `--enable-prefix-caching` - which is a far better position '
                       'than vllm-mlx, where it is off entirely. The open catch is that the '
                       'built-in MTP head and prefix caching do not yet work together.',
               'issues': ['vllm-project/vllm-metal#610',
                          'vllm-project/vllm-metal#482',
                          'vllm-project/vllm-metal#646']},
 'ds4': {'status': 'none',
         'label': 'Out of scope',
         'note': 'Not one of the three checkpoints ds4 loads.',
         'issues': []}}
