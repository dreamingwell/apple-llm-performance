"""Ornith-1.5-35B-A3B - model record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'ornith15'
MODALITY = 'text'
NAME = 'Ornith-1.5-35B-A3B'
ARCH = 'qwen3_5_moe - 36B MoE, 256 experts, 8 active (3B active)'
LICENSE = 'MIT'
CONTEXT = '262,144'
HF = 'ornith-ai/Ornith-1.5-35B-A3B'
PARAMS_B = 36
# Parameters read per decoded token, the divisor in the decode ceiling:
# published as 3B active of 36B total, 8 of 256 experts firing.
ACTIVE_PARAMS_B = 3

NOTE = (
    "The strongest thing on this page for its size, and MIT on top. SWE-bench Verified of 79 puts "
    "it within two points of DeepSeek V4 Pro at roughly a fortieth of the weight, and it does that "
    "on 3B active parameters. KV is 20 KiB/token from 10 full-attention layers out of 40 - the "
    "other 30 are linear - so a full 262k context costs about 5 GB, which is affordable on a "
    "machine that can hold the weights at all. Two things to know: it is a vision-language model, "
    "and mlx-lm's Qwen3.5 support is text-only, so the MLX path drops the image input. And the "
    "card reports Terminal-Bench 2.1 under two harnesses - 67.8 on Terminus-2, 68.5 under Claude "
    "Code - which is unusually honest, but means you should check which harness any comparison "
    "used. The figure quoted here is Terminus-2."
)

SOURCES = [('Model card with full tables', 'https://huggingface.co/ornith-ai/Ornith-1.5-35B-A3B'),
           ('Official GGUF', 'https://huggingface.co/ornith-ai/Ornith-1.5-35B-A3B-GGUF'),
           ('Official MLX', 'https://huggingface.co/ornith-ai/Ornith-1.5-35B-A3B-MLX'),
           ('Ollama library', 'https://ollama.com/library/ornith-1.5')]

SCORES = {'agentic': [('Terminal-Bench 2.1', '67.8'), ('BrowseComp', '67.6'),
                      ('GPQA Diamond', '89.2'), ('HLE (no tools)', '25.6')],
          'coding': [('SWE-bench Verified', '79.0'), ('SWE-bench Multilingual', '71.4'),
                     ('SWE-bench Pro', '59.6')]}

# Which engine the card opens on and the glance row names.
BEST_ENGINE = 'llamacpp'

# Repositories tracker/measure.py harvests for this model.
QUANT_SOURCES = {'gguf': ['ornith-ai/Ornith-1.5-35B-A3B-GGUF',
                          'bartowski/Ornith-1.5-35B-A3B-GGUF'],
                 'mlx': ['ornith-ai/Ornith-1.5-35B-A3B-MLX-8bit',
                         'ornith-ai/Ornith-1.5-35B-A3B-MLX-6bit',
                         'ornith-ai/Ornith-1.5-35B-A3B-MLX-4bit']}

# Measured by tracker/measure.py - do not hand-edit. gb is summed repo bytes;
# bpw is gb*8/PARAMS_B and is omitted for pruned or native-precision builds.
LADDER = {'gguf': [{'label': 'Ornith-1.5-35B-BF16',
           'repo': 'ornith-ai/Ornith-1.5-35B-A3B-GGUF',
           'gb': 71.07,
           'kind': 'quant',
           'bpw': 15.79},
          {'label': 'Ornith-1.5-35B-A3B-Q6_K_L',
           'repo': 'bartowski/Ornith-1.5-35B-A3B-GGUF',
           'gb': 30.77,
           'kind': 'quant',
           'bpw': 6.84},
          {'label': 'Ornith-1.5-35B-A3B-Q5_K_L',
           'repo': 'bartowski/Ornith-1.5-35B-A3B-GGUF',
           'gb': 25.81,
           'kind': 'quant',
           'bpw': 5.73},
          {'label': 'Ornith-1.5-35B-Q4_K_M',
           'repo': 'ornith-ai/Ornith-1.5-35B-A3B-GGUF',
           'gb': 21.71,
           'kind': 'quant',
           'bpw': 4.83},
          {'label': 'Ornith-1.5-35B-A3B-IQ4_XS',
           'repo': 'bartowski/Ornith-1.5-35B-A3B-GGUF',
           'gb': 19.28,
           'kind': 'quant',
           'bpw': 4.28},
          {'label': 'Ornith-1.5-35B-A3B-Q3_K_M',
           'repo': 'bartowski/Ornith-1.5-35B-A3B-GGUF',
           'gb': 16.7,
           'kind': 'quant',
           'bpw': 3.71},
          {'label': 'Ornith-1.5-35B-A3B-Q2_K_L',
           'repo': 'bartowski/Ornith-1.5-35B-A3B-GGUF',
           'gb': 13.58,
           'kind': 'quant',
           'bpw': 3.02},
          {'label': 'Ornith-1.5-35B-A3B-IQ2_M',
           'repo': 'bartowski/Ornith-1.5-35B-A3B-GGUF',
           'gb': 12.54,
           'kind': 'quant',
           'bpw': 2.79},
          {'label': 'Ornith-1.5-35B-A3B-IQ2_XXS',
           'repo': 'bartowski/Ornith-1.5-35B-A3B-GGUF',
           'gb': 10.26,
           'kind': 'quant',
           'bpw': 2.28}],
 'mlx': [{'label': 'Ornith-1.5-35B-A3B-MLX-8bit',
          'repo': 'ornith-ai/Ornith-1.5-35B-A3B-MLX-8bit',
          'gb': 36.83,
          'kind': 'quant',
          'bpw': 8.18},
         {'label': 'Ornith-1.5-35B-A3B-MLX-6bit',
          'repo': 'ornith-ai/Ornith-1.5-35B-A3B-MLX-6bit',
          'gb': 28.17,
          'kind': 'quant',
          'bpw': 6.26},
         {'label': 'Ornith-1.5-35B-A3B-MLX-4bit',
          'repo': 'ornith-ai/Ornith-1.5-35B-A3B-MLX-4bit',
          'gb': 19.51,
          'kind': 'quant',
          'bpw': 4.34}]}

# Bytes of KV per token at fp16, the context ceiling, and how it was derived.
# None for models with no growing cache (diffusion, TTS).
KV = {'bytes_per_token': 20480,
      'max_context': 262144,
      'derivation': '10 of 40 layers are full attention, one in every four; the other 30 are '
                    'linear and hold a fixed recurrent state. 2 KV heads at head_dim 256'}

# Per-engine status. Keys must be engines whose modality matches MODALITY.
ENGINES = {
    'llamacpp': {'status': 'works', 'label': 'Runs',
                 'note': "The official GGUF declares `qwen35moe`, which llama.cpp has carried since "
                         "the Qwen3.5 series landed, so this loads on a stock build rather than "
                         "needing master. bartowski publishes a second ladder if you want more "
                         "tiers than the first-party one offers.",
                 'issues': []},
    'ollama':   {'status': 'works', 'label': 'Runs',
                 'note': "In the library as a real local build, not a cloud stub: `ornith-1.5:35b` "
                         "is a 23 GB pull, with 9b at 6.6 GB and 397b at 242 GB either side of it "
                         "if you want a different size.",
                 'issues': []},
    'lmstudio': {'status': 'works', 'label': 'Runs',
                 'note': "Both engines can take it - GGUF through llama.cpp and the first-party MLX "
                         "builds through its MLX engine.",
                 'issues': []},
    'omlx':     {'status': 'works', 'label': 'Runs',
                 'note': "Serves the mlx-lm Qwen3.5 class. Text only: that class landed explicitly "
                         "without vision, so the image input this model was trained with is not "
                         "available on any MLX path.",
                 'issues': []},
    'vllmmlx':  {'status': 'works', 'label': 'Runs',
                 'note': "Wraps mlx-lm, so the same Qwen3.5 MoE class and the same text-only "
                         "limitation. 3B active makes it a reasonable continuous-batching target.",
                 'issues': []},
    'mlxlm':    {'status': 'works', 'label': 'Runs',
                 'note': "`qwen3_5_moe` has been in the models directory since 2026-02-12, and the "
                         "first-party 4, 6 and 8-bit MLX conversions are published by the model's "
                         "own authors rather than a third party.",
                 'issues': []},
    'vllmmetal': {'status': 'works', 'label': 'Runs',
                  'note': "The supported-model matrix covers the Qwen3.5 series, and 3B active over "
                          "vLLM's continuous batching is a good pairing.",
                  'issues': []},
    'ds4':      {'status': 'none', 'label': 'Out of scope',
                 'note': "ds4 is purpose-built for DeepSeek V4 and GLM-5.2 and does not carry this "
                         "architecture.",
                 'issues': []},
}
