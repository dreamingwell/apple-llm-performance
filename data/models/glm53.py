"""GLM-5.3 - model record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'glm53'
MODALITY = 'text'
NAME = 'GLM-5.3'
ARCH = 'MoE 753B total, glm_moe_dsa - 78 DSA latent-attention layers, 256 experts, 8 active'
LICENSE = 'Custom (zai-org)'
CONTEXT = '1,048,576'
HF = 'zai-org/GLM-5.3'
PARAMS_B = 753

NOTE = (
    "The flagship successor to GLM-5.2, and architecturally the same machine: `glm_moe_dsa`, 78 "
    "layers, the same 512-wide latent plus 64 rope, so the KV cost per token is identical at 88 "
    "KiB and everything that loaded 5.2 loads this. What changed is the weights and the scores - "
    "Terminal-Bench 2.1 goes from 81.0 to 88.2, which puts it within a tenth of Kimi K3 at a "
    "quarter of the size. Note the licence is no longer MIT: 5.2 was, 5.3 is a custom zai-org "
    "licence, which is a real difference if you are shipping something. At 753B this is a "
    "multi-machine model at any usable precision except ds4's Q2, which the project sizes at about "
    "197 GiB and calls resident on a 256 GB machine."
)

SOURCES = [('Model card with the full table', 'https://huggingface.co/zai-org/GLM-5.3'),
           ('config.json', 'https://huggingface.co/zai-org/GLM-5.3/raw/main/config.json'),
           ('ds4 GLM-5.3 notes', 'https://github.com/antirez/ds4#glm-53'),
           ('Z.ai', 'https://z.ai')]

SCORES = {'agentic': [('Terminal-Bench 2.1', '88.2'), ('Terminal-Bench 3.0', '28.3')],
          'coding': [('FrontierSWE', '78.1'), ('DeepSWE v1.1', '66.9'),
                     ('SWE-Marathon v1.1', '42.5')]}

# Which engine the card opens on and the glance row names.
BEST_ENGINE = 'ds4'

# Repositories tracker/measure.py harvests for this model.
QUANT_SOURCES = {'ds4': ['antirez/glm-5.3-gguf'],
                 'gguf': ['unsloth/GLM-5.3-GGUF'],
                 'mlx': []}

# Measured by tracker/measure.py - do not hand-edit. gb is summed repo bytes;
# bpw is gb*8/PARAMS_B and is omitted for pruned or native-precision builds.
LADDER = {'ds4': [{'label': 'GLM-5.3-UD-IQ2_XXS_RoutedIQ2XXS_blk78Q2K',
          'repo': 'antirez/glm-5.3-gguf',
          'gb': 211.08,
          'kind': 'quant',
          'bpw': 2.24}],
 'gguf': [{'label': 'GLM-5.3-BF16',
           'repo': 'unsloth/GLM-5.3-GGUF',
           'gb': 1507.99,
           'kind': 'quant',
           'bpw': 16.02},
          {'label': 'GLM-5.3-Q8_0',
           'repo': 'unsloth/GLM-5.3-GGUF',
           'gb': 801.36,
           'kind': 'quant',
           'bpw': 8.51},
          {'label': 'GLM-5.3-UD-Q5_K_XL',
           'repo': 'unsloth/GLM-5.3-GGUF',
           'gb': 562.47,
           'kind': 'quant',
           'bpw': 5.98},
          {'label': 'GLM-5.3-UD-Q4_K_XL',
           'repo': 'unsloth/GLM-5.3-GGUF',
           'gb': 467.29,
           'kind': 'quant',
           'bpw': 4.96},
          {'label': 'GLM-5.3-UD-Q3_K_XL',
           'repo': 'unsloth/GLM-5.3-GGUF',
           'gb': 342.97,
           'kind': 'quant',
           'bpw': 3.64},
          {'label': 'GLM-5.3-UD-IQ3_XXS',
           'repo': 'unsloth/GLM-5.3-GGUF',
           'gb': 281.69,
           'kind': 'quant',
           'bpw': 2.99},
          {'label': 'GLM-5.3-UD-Q2_K_XL',
           'repo': 'unsloth/GLM-5.3-GGUF',
           'gb': 253.88,
           'kind': 'quant',
           'bpw': 2.7},
          {'label': 'GLM-5.3-UD-IQ1_M',
           'repo': 'unsloth/GLM-5.3-GGUF',
           'gb': 228.49,
           'kind': 'quant',
           'bpw': 2.43},
          {'label': 'GLM-5.3-UD-IQ1_S',
           'repo': 'unsloth/GLM-5.3-GGUF',
           'gb': 216.72,
           'kind': 'quant',
           'bpw': 2.3}],
 'mlx': []}

# Bytes of KV per token at fp16, the context ceiling, and how it was derived.
# None for models with no growing cache (diffusion, TTS).
KV = {'bytes_per_token': 89856,
      'max_context': 1048576,
      'derivation': '78 layers of DSA latent attention, 512 + 64 rope - the same geometry as '
                    'GLM-5.2, which is why the per-token cost is identical'}

# Per-engine status. Keys must be engines whose modality matches MODALITY.
ENGINES = {
    'ds4': {'status': 'works', 'label': 'Best path',
            'note': "ds4 documents GLM-5.3 as a first-class target with its own ownership-aware Q4 "
                    "path, and publishes `antirez/glm-5.3-gguf`. Its Q2 build is about 197 GiB and "
                    "the project calls it resident on a 256 GB machine, which is the only way this "
                    "model runs on one Mac. Two 128 GB machines over RDMA is the documented "
                    "alternative. Validated on Metal.",
            'issues': []},
    'llamacpp': {'status': 'works', 'label': 'Runs',
                 'note': "Same `glm-dsa` architecture as GLM-5.2, already in the arch table, so "
                         "this loads on a stock build. unsloth publishes the GGUF ladder. The "
                         "constraint is size rather than support - at 753B every rung above Q2 "
                         "needs more memory than one Mac has.",
                 'issues': []},
    'ollama': {'status': 'works', 'label': 'Runs',
               'note': "Inherits the architecture from llama.cpp. Not in the curated library at "
                       "this size, so you are importing a GGUF yourself.",
               'issues': []},
    'lmstudio': {'status': 'works', 'label': 'Runs',
                 'note': "Its llama.cpp engine carries the architecture. Nothing curated under "
                         "lmstudio-community at this size; point it at the unsloth ladder.",
                 'issues': []},
    'omlx': {'status': 'blocked', 'label': 'No MLX build',
             'note': "oMLX serves `glm_moe_dsa` and added GLM-5.3-Flash in v0.6.3, so the "
                     "architecture is not the obstacle. Nobody has published an MLX conversion of "
                     "the full 753B model - the hub has GGUF only.",
             'issues': []},
    'mlxlm': {'status': 'blocked', 'label': 'No MLX build',
              'note': "mlx-lm has a `glm_moe_dsa` class, so this would load if a conversion "
                      "existed. None does at 753B.",
              'issues': []},
    'vllmmlx': {'status': 'blocked', 'label': 'No MLX build',
                'note': "Wraps mlx-lm, which has the class. Same missing-conversion wall.",
                'issues': []},
    'vllmmetal': {'status': 'blocked', 'label': 'Blocked',
                  'note': "Not in the supported-model matrix, and the compute layer is MLX, so it "
                          "would need a conversion that does not exist either.",
                  'issues': []},
}
