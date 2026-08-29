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
    "separate BF16 repository. Nothing on this page can load it yet - see the engine tabs."
)

SOURCES = [('Model card', 'https://huggingface.co/zai-org/GLM-5.3-Flash'),
           ('config.json', 'https://huggingface.co/zai-org/GLM-5.3-Flash/raw/main/config.json'),
           ('BF16 weights', 'https://huggingface.co/zai-org/GLM-5.3-Flash-BF16'),
           ('Z.ai', 'https://z.ai')]

SCORES = {'agentic': [], 'coding': []}

# Which engine the card opens on and the glance row names.
BEST_ENGINE = 'llamacpp'

# Repositories tracker/measure.py harvests for this model.
QUANT_SOURCES = {'gguf': ['unsloth/GLM-5.3-Flash-GGUF'],
                 'mlx': ['pipenetwork/GLM-5.3-Flash-MLX-8bit',
                         'pipenetwork/GLM-5.3-Flash-MLX-6bit',
                         'pipenetwork/GLM-5.3-Flash-MLX-4bit']}

# Measured by tracker/measure.py - do not hand-edit. gb is summed repo bytes;
# bpw is gb*8/PARAMS_B and is omitted for pruned or native-precision builds.
LADDER = {'gguf': [{'label': 'GLM-5.3-Flash-UD-Q4_K_XL',
           'repo': 'unsloth/GLM-5.3-Flash-GGUF',
           'gb': 199.71,
           'kind': 'quant',
           'bpw': 4.98},
          {'label': 'GLM-5.3-Flash-UD-IQ4_XS',
           'repo': 'unsloth/GLM-5.3-Flash-GGUF',
           'gb': 156.82,
           'kind': 'quant',
           'bpw': 3.91},
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
         {'label': 'GLM-5.3-Flash-MLX-6bit',
          'repo': 'pipenetwork/GLM-5.3-Flash-MLX-6bit',
          'gb': 255.84,
          'kind': 'quant',
          'bpw': 6.38},
         {'label': 'GLM-5.3-Flash-MLX-4bit',
          'repo': 'pipenetwork/GLM-5.3-Flash-MLX-4bit',
          'gb': 177.55,
          'kind': 'quant',
          'bpw': 4.42}]}

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
    'omlx':     {'status': 'blocked', 'label': 'Blocked',
                 'note': "Serves mlx-lm, which has no `glm5_next` model class.",
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
    'ds4':      {'status': 'none', 'label': 'Out of scope',
                 'note': "ds4 is purpose-built for DeepSeek V4 and GLM-5.2. It does not carry this "
                         "architecture.",
                 'issues': []},
 'mtplx': {'status': 'blocked',
           'label': 'Unsupported architecture',
           'note': '`glm5_next` is not in the architecture catalog, and it does not fall '
                   'through to the GLM-4 entries either - the alias match is on the model type '
                   'string, and `glm4_moe` does not appear in it. The published MLX builds do '
                   'keep `num_nextn_predict_layers: 1`, so the engine recognises that a draft '
                   'head is intended and exits with an unsupported-architecture message rather '
                   'than a missing-head one. Same wall as every other MLX engine here, reached '
                   'one step earlier.',
           'issues': []}}
