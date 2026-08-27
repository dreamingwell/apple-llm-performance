"""DeepSeek V4 Flash - model record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'v4flash'
MODALITY = 'text'
NAME = 'DeepSeek V4 Flash'
ARCH = 'MoE 284B total / 13B active · DSA sparse attention'
LICENSE = 'MIT'
CONTEXT = '1M'
HF = 'deepseek-ai/DeepSeek-V4-Flash'
PARAMS_B = 284

NOTE = ('The best shape on this page for Apple hardware: 13B active reads roughly 7.5 GB per token, '
 'so bandwidth stops being the constraint and a 256 GB machine finally does useful work. It is '
 'also the clearest example of a model whose story depends entirely on the engine - '
 'unreachable through the mainstream MLX servers, and the fastest thing here through the '
 'engine written specifically for it.')

SOURCES = [('Artificial Analysis writeup',
  'https://artificialanalysis.ai/articles/deepseek-is-back-among-the-leading-open-weights-models-with-v4-pro-and-v4-flash')]

SCORES = {'agentic': [('AA Intelligence Index', '50'), ('GDPval-AA max effort', '1388')],
 'coding': [('SWE-bench Verified', 'not published')]}

# Which engine the card opens on and the glance row names.
BEST_ENGINE = 'ds4'

# Repositories tracker/measure.py harvests for this model.
QUANT_SOURCES = {'ds4': ['antirez/deepseek-v4-gguf'],
 'gguf': ['unsloth/DeepSeek-V4-Flash-0731-GGUF'],
 'mlx': ['mlx-community/deepseek-ai-DeepSeek-V4-Flash-8bit',
         'mlx-community/DeepSeek-V4-Flash-4bit',
         'inferencerlabs/DeepSeek-V4-Flash-MLX-Q2.8-INF',
         'mlx-community/DeepSeek-V4-Flash-2bit-DQ']}

# Measured by tracker/measure.py - do not hand-edit. gb is summed repo bytes;
# bpw is gb*8/PARAMS_B and is omitted for pruned or native-precision builds.
# Some quant repos hold more than one checkpoint; a family listed here is
# filtered to files matching this pattern.
QUANT_FILTER = {'ds4': 'V4-Flash'}

LADDER = {'ds4': [{'bpw': 4.64,
          'gb': 164.6,
          'kind': 'quant',
          'label': 'DeepSeek-V4-Flash-Q4KExperts-F16HC-F16Compressor-F16Indexer-Q8Attn-Q8Shared-Q8Out-chat-v2',
          'repo': 'antirez/deepseek-v4-gguf'},
         {'bpw': 4.39,
          'gb': 156.0,
          'kind': 'quant',
          'label': 'DeepSeek-V4-Flash-MXFP4Experts-F16HC-F16Compressor-F16Indexer-Q8Attn-Q8Shared-Q8Out-chat-v2-mxfp4-0731',
          'repo': 'antirez/deepseek-v4-gguf'},
         {'bpw': 2.44,
          'gb': 86.7,
          'kind': 'quant',
          'label': 'DeepSeek-V4-Flash-IQ2XXS-w2Q2K-AProjQ8-SExpQ8-OutQ8-chat-v2',
          'repo': 'antirez/deepseek-v4-gguf'}],
 'gguf': [{'bpw': 4.56,
           'gb': 161.9,
           'kind': 'quant',
           'label': 'DeepSeek-V4-Flash-0731-UD-Q8_K_XL',
           'repo': 'unsloth/DeepSeek-V4-Flash-0731-GGUF'},
          {'bpw': 4.37,
           'gb': 155.1,
           'kind': 'quant',
           'label': 'DeepSeek-V4-Flash-0731-UD-Q4_K_XL',
           'repo': 'unsloth/DeepSeek-V4-Flash-0731-GGUF'},
          {'bpw': 3.85,
           'gb': 136.7,
           'kind': 'quant',
           'label': 'DeepSeek-V4-Flash-0731-UD-IQ4_NL',
           'repo': 'unsloth/DeepSeek-V4-Flash-0731-GGUF'},
          {'bpw': 3.61,
           'gb': 128.2,
           'kind': 'quant',
           'label': 'DeepSeek-V4-Flash-0731-UD-Q3_K_XL',
           'repo': 'unsloth/DeepSeek-V4-Flash-0731-GGUF'},
          {'bpw': 3.27,
           'gb': 116.1,
           'kind': 'quant',
           'label': 'DeepSeek-V4-Flash-0731-UD-IQ3_S',
           'repo': 'unsloth/DeepSeek-V4-Flash-0731-GGUF'},
          {'bpw': 2.73,
           'gb': 96.8,
           'kind': 'quant',
           'label': 'DeepSeek-V4-Flash-0731-UD-Q2_K_XL',
           'repo': 'unsloth/DeepSeek-V4-Flash-0731-GGUF'},
          {'bpw': 2.56,
           'gb': 90.9,
           'kind': 'quant',
           'label': 'DeepSeek-V4-Flash-0731-UD-IQ2_M',
           'repo': 'unsloth/DeepSeek-V4-Flash-0731-GGUF'},
          {'bpw': 2.45,
           'gb': 86.9,
           'kind': 'quant',
           'label': 'DeepSeek-V4-Flash-0731-UD-IQ1_M',
           'repo': 'unsloth/DeepSeek-V4-Flash-0731-GGUF'},
          {'bpw': 2.33,
           'gb': 82.5,
           'kind': 'quant',
           'label': 'DeepSeek-V4-Flash-0731-UD-IQ1_S',
           'repo': 'unsloth/DeepSeek-V4-Flash-0731-GGUF'}],
 'mlx': [{'bpw': 8.51,
          'gb': 302.27,
          'kind': 'quant',
          'label': 'deepseek-ai-DeepSeek-V4-Flash-8bit',
          'repo': 'mlx-community/deepseek-ai-DeepSeek-V4-Flash-8bit'},
         {'bpw': 4.27,
          'gb': 151.48,
          'kind': 'quant',
          'label': 'DeepSeek-V4-Flash-4bit',
          'repo': 'mlx-community/DeepSeek-V4-Flash-4bit'},
         {'bpw': 2.88,
          'gb': 102.2,
          'kind': 'quant',
          'label': 'DeepSeek-V4-Flash-MLX-Q2.8-INF',
          'repo': 'inferencerlabs/DeepSeek-V4-Flash-MLX-Q2.8-INF'},
         {'bpw': 2.72,
          'gb': 96.52,
          'kind': 'quant',
          'label': 'DeepSeek-V4-Flash-2bit-DQ',
          'repo': 'mlx-community/DeepSeek-V4-Flash-2bit-DQ'}]}

# Bytes of KV per token at fp16, the context ceiling, and how it was derived.
# None for models with no growing cache (diffusion, TTS).
KV = {'bytes_per_token': 49536,
 'max_context': 1048576,
 'derivation': '43 layers of DSA latent attention, 512 + 64 rope'}

# Per-engine status. Keys must be engines whose modality matches MODALITY.
ENGINES = {'vllmmetal': {'status': 'blocked',
               'label': 'Blocked',
               'note': 'Not in the support matrix. Latent attention generally is the weak spot '
                       'here: the only MLA row carried is flagged as having no Metal kernel, '
                       'and a specialised MLA paged-attention kernel is still at the RFC '
                       'stage.',
               'issues': ['vllm-project/vllm-metal#360']},
 'ds4': {'status': 'works',
         'label': 'Best path',
         'note': 'This is what ds4 exists for, and it is the strongest single answer on this '
                 'page. Purpose-built C and Metal kernels for one architecture, with measured '
                 'Metal numbers rather than estimates: 790 tok/s prefill and 39.4 tok/s '
                 'generation at 2k context on a 128 GB M5 Max at q2, still 27.6 tok/s at 64k. '
                 "Choose your fit - 86.7 GB at IQ2_XXS, 156 GB keeping DeepSeek's native MXFP4 "
                 'experts, 164.6 GB at Q4K. `ds4-server` speaks both OpenAI and Anthropic, '
                 'persists KV to disk across restarts, and `--batched-session N` gives you '
                 'real concurrent sessions. The open issues to read first are both '
                 'agent-shaped: O(n squared) tokenization on large prompts, and stateless '
                 'clients failing to extend the live KV session.',
         'issues': ['antirez/ds4#853',
                    'antirez/ds4#816',
                    'antirez/ds4#836',
                    'antirez/ds4#805',
                    'antirez/ds4#851',
                    'antirez/ds4#839']},
 'llamacpp': {'status': 'degraded',
              'label': 'Runs, degraded',
              'note': '`deepseek4` landed in mainline, so this works without a fork - but the '
                      'open issues are unusually well aimed at agent use. The tokenizer '
                      'overflows its stack on long tool output, tool calls with similar '
                      'parameter names error out, there is a report of the model silently '
                      'forgetting earlier context, and one of a 200-second prefill for a '
                      '10-token prompt. If you want this model, ds4 is the engine that was '
                      'built for it.',
              'issues': ['ggml-org/llama.cpp#26965',
                         'ggml-org/llama.cpp#25171',
                         'ggml-org/llama.cpp#25796',
                         'ggml-org/llama.cpp#25744']},
 'ollama': {'status': 'works',
            'label': 'Runs',
            'note': 'In the library as `deepseek-v4-flash`. The zero-effort route; the ceiling '
                    "is lower than ds4's and you inherit whichever backend the tag resolves "
                    'to.',
            'issues': []},
 'lmstudio': {'status': 'works',
              'label': 'Runs',
              'note': 'Runs through the GGUF engine with the llama.cpp caveats above. Not '
                      'through its MLX engine - there is no mlx-lm model class to use.',
              'issues': []},
 'omlx': {'status': 'degraded',
          'label': 'Runs, degraded',
          'note': 'oMLX does load DeepSeek V4 Flash, which no mlx-lm-derived engine can - so '
                  'it has its own path. Speed is the problem: 4-17 tok/s on a 128 GB M5 Max, '
                  'traced to the bundled MLX keeping a single residency set so weights fault '
                  'instead of staying wired. On top of that, MXFP4 crashes on float32 '
                  'activations, the prefix cache drops out with a signature mismatch, and '
                  'thinking leaks into content on truncated turns. ds4 gets roughly ten times '
                  'the decode rate on comparable hardware.',
          'issues': ['jundot/omlx#3121',
                     'jundot/omlx#2469',
                     'jundot/omlx#2493',
                     'jundot/omlx#2606']},
 'vllmmlx': {'status': 'blocked',
             'label': 'Blocked',
             'note': 'The quant exists and the footprint is ideal - 13B active reads about 7.5 '
                     'GB per token, so bandwidth stops being the constraint - but the '
                     'architecture is rejected outright. There is nothing to wrap: mlx-lm has '
                     'no deepseek_v4 model class.',
             'issues': ['waybarrios/vllm-mlx#668',
                        'ml-explore/mlx-lm#1233',
                        'ml-explore/mlx-lm#1332']},
 'mlxlm': {'status': 'blocked',
           'label': 'Blocked',
           'note': 'The single most consequential gap in MLX. Several quants exist and their '
                   'cards tell you to `pip install mlx-lm`, but there is no `deepseek_v4.py` '
                   'in mlx-lm - support is PR #1233, still open. The residency-growth issue '
                   "that aborts decode after about 11k tokens is filed against that PR's head, "
                   'not against a released version. If you want an MLX-shaped route anyway, '
                   '[ssd-moe/deepseek-v4-flash-mlx](https://github.com/ssd-moe/deepseek-v4-flash-mlx) '
                   'is a custom MLX offload engine that streams experts from SSD to run this '
                   "on a 48 GB Mac at about 4.5-5 tok/s - a different tradeoff from ds4's own "
                   'SSD streaming, and far slower than either resident path.',
           'issues': ['ml-explore/mlx-lm#1233',
                      'ml-explore/mlx-lm#1332',
                      'ml-explore/mlx-lm#1192',
                      'ml-explore/mlx-lm#1281',
                      'ml-explore/mlx-lm#1443',
                      'ml-explore/mlx-lm#1662',
                      'ml-explore/mlx-lm#1404']}}
