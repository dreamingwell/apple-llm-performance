"""GLM-5.3-Flash - model record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'glm53f'
MODALITY = 'text'
NAME = 'GLM-5.3-Flash'
ARCH = 'glm5_next - 321B MoE, 288 routed experts, 8 active + 1 shared'
LICENSE = 'MIT'
CONTEXT = '1,048,576'
HF = 'zai-org/GLM-5.3-Flash'
PARAMS_B = 321

NOTE = (
    "Released 2026-08-25 under MIT, which is unusually permissive for a model this size. It is a "
    "middle tier rather than a successor to GLM-5.2: 321B against 5.2's 744B, so it is aimed at "
    "machines that cannot hold the flagship. The architecture is the interesting part - 45 layers "
    "of which only 11 are full attention, the other 34 being KDA linear attention, and those 11 "
    "store a 512-wide latent vector rather than separate K and V. That is roughly 11 KB of cache "
    "per token, about a fifth of what DeepSeek V4 Flash needs and an eighth of GLM-5.2, which is "
    "the whole point of the Flash line. It is also a vision-language model; the config carries "
    "image and video token ids alongside the text stack. Weights ship pre-quantised to FP8, with a "
    "separate BF16 repository. oMLX vendored support for it in v0.6.3 within two days of release, and is currently the only engine here that can load it - see the engine tabs."
)

SOURCES = [('Model card', 'https://huggingface.co/zai-org/GLM-5.3-Flash'),
           ('config.json', 'https://huggingface.co/zai-org/GLM-5.3-Flash/raw/main/config.json'),
           ('BF16 weights', 'https://huggingface.co/zai-org/GLM-5.3-Flash-BF16'),
           ('Z.ai', 'https://z.ai')]

SCORES = {'agentic': [], 'coding': []}

# Which engine the card opens on and the glance row names.
BEST_ENGINE = 'omlx'

# Repositories tracker/measure.py harvests for this model.
QUANT_SOURCES = {'gguf': ['unsloth/GLM-5.3-Flash-GGUF'],
                 'mlx': ['Jundot/GLM-5.3-Flash-oQ4e',
                         'pipenetwork/GLM-5.3-Flash-MLX-8bit',
                         'pipenetwork/GLM-5.3-Flash-MLX-4bit',
                         'Vontra/GLM-5.3-Flash-MLX-4bit-MTP'],
                 'ds4': ['antirez/glm-5.3-flash-gguf']}

# Measured by tracker/measure.py - do not hand-edit. gb is summed repo bytes;
# bpw is gb*8/PARAMS_B and is omitted for pruned or native-precision builds.
LADDER = {'gguf': [{'label': 'GLM-5.3-Flash-BF16',
           'repo': 'unsloth/GLM-5.3-Flash-GGUF',
           'gb': 641.64,
           'kind': 'quant',
           'bpw': 15.99},
          {'label': 'GLM-5.3-Flash-Q8_0',
           'repo': 'unsloth/GLM-5.3-Flash-GGUF',
           'gb': 340.98,
           'kind': 'quant',
           'bpw': 8.5},
          {'label': 'GLM-5.3-Flash-UD-Q5_K_XL',
           'repo': 'unsloth/GLM-5.3-Flash-GGUF',
           'gb': 240.31,
           'kind': 'quant',
           'bpw': 5.99},
          {'label': 'GLM-5.3-Flash-UD-Q4_K_XL',
           'repo': 'unsloth/GLM-5.3-Flash-GGUF',
           'gb': 199.71,
           'kind': 'quant',
           'bpw': 4.98},
          {'label': 'GLM-5.3-Flash-UD-Q3_K_XL',
           'repo': 'unsloth/GLM-5.3-Flash-GGUF',
           'gb': 147.54,
           'kind': 'quant',
           'bpw': 3.68},
          {'label': 'GLM-5.3-Flash-UD-IQ3_XXS',
           'repo': 'unsloth/GLM-5.3-Flash-GGUF',
           'gb': 120.37,
           'kind': 'quant',
           'bpw': 3.0},
          {'label': 'GLM-5.3-Flash-UD-Q2_K_XL',
           'repo': 'unsloth/GLM-5.3-Flash-GGUF',
           'gb': 108.72,
           'kind': 'quant',
           'bpw': 2.71},
          {'label': 'GLM-5.3-Flash-UD-IQ1_M',
           'repo': 'unsloth/GLM-5.3-Flash-GGUF',
           'gb': 97.58,
           'kind': 'quant',
           'bpw': 2.43},
          {'label': 'GLM-5.3-Flash-UD-IQ1_S',
           'repo': 'unsloth/GLM-5.3-Flash-GGUF',
           'gb': 93.09,
           'kind': 'quant',
           'bpw': 2.32}],
 'mlx': [{'label': 'GLM-5.3-Flash-MLX-8bit',
          'repo': 'pipenetwork/GLM-5.3-Flash-MLX-8bit',
          'gb': 334.13,
          'kind': 'quant',
          'bpw': 8.33},
         {'label': 'GLM-5.3-Flash-MLX-4bit-MTP',
          'repo': 'Vontra/GLM-5.3-Flash-MLX-4bit-MTP',
          'gb': 181.71,
          'kind': 'quant',
          'bpw': 4.53}],
 'ds4': [{'label': 'GLM-5.3-Flash-FP8',
          'repo': 'antirez/glm-5.3-flash-gguf',
          'gb': 327.21,
          'kind': 'quant',
          'bpw': 8.15},
         {'label': 'GLM-5.3-Flash-Q4_K',
          'repo': 'antirez/glm-5.3-flash-gguf',
          'gb': 190.88,
          'kind': 'quant',
          'bpw': 4.76},
         {'label': 'GLM-5.3-Flash-Q2',
          'repo': 'antirez/glm-5.3-flash-gguf',
          'gb': 96.51,
          'kind': 'quant',
          'bpw': 2.41}]}

# Bytes of KV per token at fp16, the context ceiling, and how it was derived.
# None for models with no growing cache (diffusion, TTS).
KV = {'bytes_per_token': 11264,
      'max_context': 1048576,
      'derivation': '11 of 45 layers are full attention (the config names them explicitly); the '
                    'other 34 are KDA linear and hold a fixed recurrent state. Each full layer '
                    'stores one 512-wide latent vector, with no separate rope dimension'}

# Per-engine status. Keys must be engines whose modality matches MODALITY.
ENGINES = {
    'llamacpp': {'status': 'blocked', 'label': 'Blocked',
                 'note': "`glm5_next` is not in `src/llama-arch.cpp`. Three competing PRs are open "
                         "for it - #27752, #27754 and #27773 - which is a good sign of demand and a "
                         "bad sign for a settled implementation. GGUFs are already published, so "
                         "the files exist ahead of the loader.",
                 'issues': ['ggml-org/llama.cpp#27752']},
    'ollama':   {'status': 'blocked', 'label': 'Blocked',
                 'note': "Ollama takes this architecture from llama.cpp, so it is blocked until "
                         "that lands and Ollama bumps. Not in the library.",
                 'issues': []},
    'lmstudio': {'status': 'blocked', 'label': 'Blocked',
                 'note': "Both of LM Studio's engines are downstream here: its llama.cpp build has "
                         "no `glm5_next`, and its MLX engine has no mlx-lm class to call.",
                 'issues': []},
    'omlx':     {'status': 'degraded', 'label': 'Only path',
                 'note': "oMLX added first-class GLM-5.3-Flash support in v0.6.3 on 2026-08-27, "
                         "alongside Qwen3.8-Flash-Next, with its own implementation rather than "
                         "waiting for mlx-lm - so this is the only engine here that can load the "
                         "model at all. The maintainer's M3 Ultra 512 GB figures are 482 tok/s "
                         "prefill and 24.1 tok/s generation at 4k, holding 450 and 23.5 at 32k, at "
                         "about 179 GiB resident. There is a first-party `Jundot/GLM-5.3-Flash-oQ4e` "
                         "build. Text and image input; video is unsupported. The open Qwen4-Exp "
                         "defects on this engine do not apply here - they are in the vendored "
                         "qwen4_exp path, not the GLM one.",
                 'issues': []},
    'vllmmlx':  {'status': 'blocked', 'label': 'Blocked',
                 'note': "No `glm5_next` support. The MLX quants on the hub were converted ahead of "
                         "any runtime that can execute them.",
                 'issues': []},
    'mlxlm':    {'status': 'blocked', 'label': 'Blocked',
                 'note': "No `mlx_lm/models/glm5_next.py`, so mlx-lm refuses the weights whichever "
                         "quant you point it at. This is the gate for every MLX engine here.",
                 'issues': []},
    'vllmmetal': {'status': 'blocked', 'label': 'Blocked',
                  'note': "Not in `docs/supported_models.md`, and the compute layer is MLX, so it "
                          "inherits the missing model class.",
                  'issues': []},
    'ds4':      {'status': 'works', 'label': 'Purpose-built',
                 'note': 'ds4 has a dedicated GLM-5.3-Flash implementation, not a generic path: '
                          'its own graph for the recurrent KDA and sparse DSA layers, its own '
                          'published artifacts, and a documented section of the README. '
                          '`antirez/glm-5.3-flash-gguf` carries Q2 at 96.5 GB, Q4_K at 190.9 GB '
                          'and FP8 at 327.2 GB, plus a separate 1.1 GB vision encoder that the '
                          'text GGUF does not include - pass it with `--vision`. MTP is '
                          'supported, and two 128 GB machines can run it over RDMA. That makes '
                          'Q2 the one build here that fits a single 128 GB Mac.',
                 'issues': []},
}
