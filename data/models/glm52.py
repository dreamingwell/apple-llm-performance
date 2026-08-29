"""GLM-5.2 - model record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'glm52'
MODALITY = 'text'
NAME = 'GLM-5.2'
ARCH = 'MoE 744B total / 40B active · glm_moe_dsa + IndexShare'
LICENSE = 'MIT'
CONTEXT = '1M'
HF = 'zai-org/GLM-5.2'
PARAMS_B = 744
# Parameters read per decoded token, the divisor in the decode ceiling:
# published as 40B active of 744B total.
ACTIVE_PARAMS_B = 40

NOTE = ('The highest agentic score reachable on Apple hardware, and reachable today - just not '
 'through the MLX servers, which are blocked three ways. The practical constraints are size '
 'and precision: the builds that fit one or two Macs are 1-2 bit, so the honest question is '
 'not whether it loads but how much of the model survives the quantisation.')

SOURCES = [('Artificial Analysis writeup',
  'https://artificialanalysis.ai/articles/glm-5-2-is-the-new-leading-open-weights-model-on-the-artificial-analysis-intelligence-index'),
 ('Model card', 'https://huggingface.co/zai-org/GLM-5.2')]

SCORES = {'agentic': [('Terminal-Bench 2.1', '81.0')],
 'coding': [('SWE-bench Pro', '62.1%'), ('DeepSWE', '46.2'), ('AIME 2026', '99.2')]}

# Which engine the card opens on and the glance row names.
BEST_ENGINE = 'ds4'

# Repositories tracker/measure.py harvests for this model.
QUANT_SOURCES = {'ds4': ['antirez/glm-5.2-gguf'],
 'gguf': ['unsloth/GLM-5.2-GGUF'],
 'mlx': ['mlx-community/GLM-5.2-DQ4plus-q8',
         'mlx-community/GLM-5.2-4bit',
         'mlx-community/GLM-5.2-mxfp4',
         'pipenetwork/GLM-5.2-MLX-mixed-3_6bit']}

# Measured by tracker/measure.py - do not hand-edit. gb is summed repo bytes;
# bpw is gb*8/PARAMS_B and is omitted for pruned or native-precision builds.
LADDER = {'ds4': [{'bpw': 4.67,
          'gb': 434.2,
          'kind': 'quant',
          'label': 'GLM-5.2-UD-Q4_K_RoutedQ4K',
          'repo': 'antirez/glm-5.2-gguf'},
         {'bpw': 2.82,
          'gb': 262.0,
          'kind': 'quant',
          'label': 'GLM-5.2-UD-Q2_K_RoutedQ2K',
          'repo': 'antirez/glm-5.2-gguf'},
         {'bpw': 2.27,
          'gb': 211.1,
          'kind': 'quant',
          'label': 'GLM-5.2-UD-IQ2_XXS_RoutedIQ2XXS_blk78Q2K',
          'repo': 'antirez/glm-5.2-gguf'}],
 'gguf': [{'bpw': 16.21,
           'gb': 1508.0,
           'kind': 'quant',
           'label': 'GLM-5.2-BF16',
           'repo': 'unsloth/GLM-5.2-GGUF'},
          {'bpw': 7.36,
           'gb': 684.4,
           'kind': 'quant',
           'label': 'GLM-5.2-UD-Q6_K_XL',
           'repo': 'unsloth/GLM-5.2-GGUF'},
          {'bpw': 6.05,
           'gb': 562.5,
           'kind': 'quant',
           'label': 'GLM-5.2-UD-Q5_K_XL',
           'repo': 'unsloth/GLM-5.2-GGUF'},
          {'bpw': 5.02,
           'gb': 467.3,
           'kind': 'quant',
           'label': 'GLM-5.2-UD-Q4_K_XL',
           'repo': 'unsloth/GLM-5.2-GGUF'},
          {'bpw': 4.01,
           'gb': 372.7,
           'kind': 'quant',
           'label': 'GLM-5.2-UD-IQ4_NL',
           'repo': 'unsloth/GLM-5.2-GGUF'},
          {'bpw': 3.69,
           'gb': 343.0,
           'kind': 'quant',
           'label': 'GLM-5.2-UD-Q3_K_XL',
           'repo': 'unsloth/GLM-5.2-GGUF'},
          {'bpw': 3.03,
           'gb': 281.7,
           'kind': 'quant',
           'label': 'GLM-5.2-UD-IQ3_XXS',
           'repo': 'unsloth/GLM-5.2-GGUF'},
          {'bpw': 2.57,
           'gb': 238.6,
           'kind': 'quant',
           'label': 'GLM-5.2-UD-IQ2_M',
           'repo': 'unsloth/GLM-5.2-GGUF'},
          {'bpw': 2.33,
           'gb': 216.7,
           'kind': 'quant',
           'label': 'GLM-5.2-UD-IQ1_S',
           'repo': 'unsloth/GLM-5.2-GGUF'}],
 'mlx': [{'bpw': 5.0,
          'gb': 464.61,
          'kind': 'quant',
          'label': 'GLM-5.2-DQ4plus-q8',
          'repo': 'mlx-community/GLM-5.2-DQ4plus-q8'},
         {'bpw': 4.5,
          'gb': 418.32,
          'kind': 'quant',
          'label': 'GLM-5.2-4bit',
          'repo': 'mlx-community/GLM-5.2-4bit'},
         {'bpw': 4.25,
          'gb': 395.09,
          'kind': 'quant',
          'label': 'GLM-5.2-mxfp4',
          'repo': 'mlx-community/GLM-5.2-mxfp4'},
         {'bpw': 3.57,
          'gb': 332.34,
          'kind': 'quant',
          'label': 'GLM-5.2-MLX-mixed-3_6bit',
          'repo': 'pipenetwork/GLM-5.2-MLX-mixed-3_6bit'}]}

# Bytes of KV per token at fp16, the context ceiling, and how it was derived.
# None for models with no growing cache (diffusion, TTS).
KV = {'bytes_per_token': 89856,
 'max_context': 1048576,
 'derivation': '78 layers of DSA latent attention, 512 + 64 rope'}

# Published throughput measurements: someone else's numbers, with whose they are.
# Never crowd-sourced and never estimated - see notes/tokens-per-second.md for the
# bar a record has to clear, and tracker/throughput.py for what the page derives.
SPEEDS = [
 {'engine': 'omlx', 'chip': 'm3ultra', 'mem_gb': 512, 'build': 'GLM-5.2-mxfp4',
  'prefill_tps': 845,
  'who': 'oMLX published figure, contested in jundot/omlx#3006',
  'url': 'https://github.com/jundot/omlx/issues/3006',
  'note': 'Prefill, not decode, and this page does not derive prefill at all - prefill is a '
          'batched matmul over the whole prompt, so it is compute-bound and the bandwidth '
          'argument does not apply to it. The figure holds only with the native DSA kernels '
          'compiled in.'},
 {'engine': 'omlx', 'chip': 'm3ultra', 'mem_gb': 512, 'build': 'GLM-5.2-mxfp4',
  'prefill_tps': 29,
  'who': 'jundot/omlx#3006 reporters, fallback kernels',
  'url': 'https://github.com/jundot/omlx/issues/3006',
  'note': 'The same model on the same chip with the fallback path, which is what a plain '
          'pip install gives you. A 29x gap between two correct measurements of the same '
          'thing is the reason a bare tokens-per-second number is worth so little without '
          'the build it came from.'},
]

# Per-engine status. Keys must be engines whose modality matches MODALITY.
ENGINES = {'vllmmetal': {'status': 'blocked',
               'label': 'Blocked',
               'note': "Not in the matrix. GLM-5.2's DSA attention is a latent-attention "
                       'variant, and the MLA Metal kernel it would need is an open RFC.',
               'issues': ['vllm-project/vllm-metal#360']},
 'ds4': {'status': 'works',
         'label': 'Best path',
         'note': 'The highest agentic score reachable on Apple hardware, and ds4 is how you '
                 'reach it. The routed IQ2_XXS build is 211.1 GB in one file, Q2_K is 262 GB, '
                 'Q4_K is 434.2 GB. The interesting mode is tensor parallelism over '
                 'Thunderbolt: two Macs hold half the routed experts each and work on the same '
                 'token together, which cuts latency rather than just fitting a bigger model - '
                 'demonstrated on a pair of 128 GB MacBooks. It needs an IQ2_XXS or Q2_K '
                 'routed layout, so a routed Q4 GLM is rejected for that mode, and RDMA needs '
                 'an IPv4 address on the cabled interface itself rather than the bridge.',
         'issues': ['antirez/ds4#845',
                    'antirez/ds4#853',
                    'antirez/ds4#816',
                    'antirez/ds4#836',
                    'antirez/ds4#805',
                    'antirez/ds4#839']},
 'omlx': {'status': 'degraded',
          'label': 'Runs, degraded',
          'note': 'oMLX ships fused DSA prefill kernels for GLM-5.2, and with them the '
                  'difference is not marginal: 845 tok/s versus about 29 on an M3 Ultra. The '
                  'trap is that a plain `pip install` does not build them and the fallback is '
                  'silent, so most people measuring this model on oMLX are measuring the wrong '
                  'thing. Use the DMG or build with full Xcode. Open on top of that: '
                  'repetition loops, mxfp4 failing to load on 0.4.4, and prefill throttling '
                  'near the memory ceiling.',
          'issues': ['jundot/omlx#3006',
                     'jundot/omlx#2099',
                     'jundot/omlx#1927',
                     'jundot/omlx#2208',
                     'jundot/omlx#2137']},
 'llamacpp': {'status': 'works',
              'label': 'Runs',
              'note': '`glm-dsa` is in mainline. The quant ladder is the whole story: IQ1_S '
                      '216.7 GB, IQ2_XXS 238.5 GB, Q2_K_XL 253.9 GB, and Q4 tiers from 436 GB '
                      'up - so a single 256 GB machine reaches only the 1-2 bit tiers, and '
                      'quality at IQ1 is a real question rather than a footnote. One '
                      'structural annoyance: DSA has no V cache, but the K and V cache types '
                      'are validated as a pair, so you cannot quantise K independently on the '
                      'model with the least memory to spare.',
              'issues': ['ggml-org/llama.cpp#26382']},
 'ollama': {'status': 'works',
            'label': 'Runs',
            'note': 'In the library. On a single 256 GB machine you will need to be deliberate '
                    'about the tag - the Q2-class build is already at 254 GB before any KV.',
            'issues': []},
 'lmstudio': {'status': 'works',
              'label': 'Runs',
              'note': 'GGUF engine only in practice. The MLX build exists but mlx-lm cannot '
                      "load it, and LM Studio's MLX engine is downstream of that.",
              'issues': []},
 'vllmmlx': {'status': 'blocked',
             'label': 'Blocked',
             'note': 'Blocked three ways through mlx-lm: the IndexShare indexers fail to load, '
                     'DSA top-k evicts attention sinks, and at a measured 395.1 GB it sits '
                     'squarely inside the >300 GB band where a one-shot mx.eval trips the GPU '
                     'watchdog at load.',
             'issues': ['ml-explore/mlx-lm#1418',
                        'ml-explore/mlx-lm#1443',
                        'ml-explore/mlx-lm#1572']},
 'mlxlm': {'status': 'blocked',
           'label': 'Blocked',
           'note': '`glm_moe_dsa.py` exists, but the model does not load: IndexShare indexers, '
                   'sink eviction under DSA top-k, and the >300 GB load watchdog.',
           'issues': ['ml-explore/mlx-lm#1418',
                      'ml-explore/mlx-lm#1443',
                      'ml-explore/mlx-lm#1572']}}
