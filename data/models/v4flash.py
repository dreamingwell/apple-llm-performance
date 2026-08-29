"""DeepSeek V4 Flash - model record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'v4flash'
MODALITY = 'text'
NAME = 'DeepSeek V4 Flash'
ARCH = 'MoE 284B total / 13B active · DSA sparse attention'
LICENSE = 'MIT'
CONTEXT = '1M'
HF = 'deepseek-ai/DeepSeek-V4-Flash-0731'
PARAMS_B = 284

NOTE = ('The best shape on this page for Apple hardware: 13B active reads roughly 7.5 GB per token, '
 'so bandwidth stops being the constraint and a 256 GB machine finally does useful work. It is '
 'also the clearest example of a model whose story depends entirely on the engine - '
 'unreachable through the mainstream MLX servers, and carried by one engine written '
 'specifically for it. Read both engine tabs before committing: ds4 is the default here, '
 'but llama.cpp runs this on a stock build and the case between them is narrower than a '
 'single recommendation makes it look.')

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
         'note': 'Purpose-built C and Metal kernels for this one architecture, and the only '
                  'engine here with published Metal numbers for it. Be precise about which '
                  'numbers: the headline 790 tok/s prefill and 39.4 tok/s generation are q2 on a '
                  '128 GB M5 Max. The build a 256 GB machine would actually load is q4, and the '
                  'only q4 figure the project publishes is from its older sweep - 35.5 tok/s '
                  'generation on a 512 GB M3 Ultra, against 36.9 for q2 on the same machine, so '
                  'the quant costs little. There is no head-to-head against llama.cpp on Metal, '
                  'by anyone. `ds4-server` speaks OpenAI and Anthropic, persists KV to disk '
                  'across restarts, and `--batched-session N` gives real concurrent sessions. '
                  'Its own costs are real: the BPE merge loop is O(n squared), so a 24k-token '
                  'prompt burns 175-250 seconds of CPU before prefill even starts - measured on '
                  'an M3 Ultra, and worse for agents than anything llama.cpp has on Metal - '
                  'there are no tagged releases, and vision is unsupported.',
         'issues': ['antirez/ds4#853', 'antirez/ds4#816', 'antirez/ds4#836', 'antirez/ds4#805', 'antirez/ds4#851', 'antirez/ds4#839']},
 'llamacpp': {'status': 'degraded',
              'label': 'Runs, degraded',
              'note': '`deepseek4` is in mainline, so this works on a stock build, and at 256 '
                       'GB the GGUF ladder gives you more rungs to choose from than ds4 does. '
                       'The reason it is not the default here is one open defect, and it is '
                       'filed against exactly this case: a Mac Studio M3 Ultra with 256 GB '
                       'running the unsloth UD-Q8_K_XL build on Metal degenerates into '
                       'repetition and leaks special tokens over a long agentic session. It '
                       'degrades rather than fails, so a short test will not show it. For one- '
                       'shot or short-conversation use the two engines are much closer than this '
                       'page previously implied.',
              'issues': ['ggml-org/llama.cpp#26694']},
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
          'note': 'oMLX does load DeepSeek V4 Flash, which no mlx-lm-derived engine can, so it '
                   'has its own path. The residency thrash that held decode to 4-17 tok/s on a '
                   '128 GB M5 Max was closed as fixed on 2026-08-28 with the v0.6.3 release; '
                   'nobody has published a decode figure since, so the old number is historical '
                   'and the new one is unmeasured. Three defects behind this status are still '
                   'open: MXFP4 crashes on float32 activations, the prefix cache drops out with '
                   'a signature mismatch and takes a severe slowdown with it, and thinking leaks '
                   'into content on truncated turns. ds4 remains the faster path on comparable '
                   'hardware.',
          'issues': ['jundot/omlx#3121', 'jundot/omlx#2469', 'jundot/omlx#2493', 'jundot/omlx#2606']},
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
                    'cards tell you to `pip install mlx-lm`, but there is no `deepseek_v4.py` in '
                    'mlx-lm - support is PR #1233, still open. The residency growth that used to '
                    'abort decode at around 11k tokens is no longer the blocker: #1784 and #1790 '
                    'fixed it upstream on 2026-08-27. Only the missing model class stands '
                    'between this and running. If you want an MLX-shaped route meanwhile, [ssd- '
                    'moe/deepseek-v4-flash-mlx](https://github.com/ssd-moe/deepseek-v4-flash- '
                    'mlx) is a custom MLX offload engine that streams experts from SSD to run '
                    "this on a 48 GB Mac at about 4.5-5 tok/s - a different tradeoff from ds4's "
                    'own SSD streaming, and far slower than either resident path.',
           'issues': ['ml-explore/mlx-lm#1233', 'ml-explore/mlx-lm#1332', 'ml-explore/mlx-lm#1192', 'ml-explore/mlx-lm#1281', 'ml-explore/mlx-lm#1443', 'ml-explore/mlx-lm#1662', 'ml-explore/mlx-lm#1404']},
 'mtplx': {'status': 'degraded',
           'label': 'Runs, no MTP',
           'note': 'The surprise on this row. MTPLX carries a 4,300-line from-scratch MLX port '
                   'of DeepSeek V4 - Hyper-Connections, compressed sparse attention, '
                   "hash-routed MoE and grouped output-LoRA, transcribed from DeepSeek's "
                   'reference implementation - so it loads the mlx-community checkpoints '
                   'directly, with no mlx-lm model class involved. It shipped in 2.4.2 on '
                   '2026-08-02. What you will not get is the speculative decoding this engine '
                   'exists for: all four MLX repos measured above declare '
                   '`num_nextn_predict_layers: 1` and then ship zero `mtp.*` tensors, so the '
                   'run degrades to plain autoregressive with a message saying so. The project '
                   'reports K=1-3 reaching 2.28x on a 2bit-DQ build carrying the draft weights; '
                   'the only published MLX build that actually carries them is '
                   '`Jundot/DeepSeek-V4-Flash-0731-oQ2e-mtp`, with 114 `mtp.0.*` tensors, and '
                   'it is not on this ladder. The backend is labelled experimental in the '
                   'registry.',
           'issues': []}}
