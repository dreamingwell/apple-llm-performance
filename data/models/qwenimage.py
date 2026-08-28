"""Qwen-Image - model record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'qwenimage'
MODALITY = 'image'
NAME = 'Qwen-Image'
ARCH = '20B MMDiT, base (not distilled)'
LICENSE = 'Apache-2.0'
CONTEXT = '1024x1024 typical, 30 steps'
CONTEXT_LABEL = 'Output'
HF = 'Qwen/Qwen-Image'
PARAMS_B = 20

NOTE = (
    "The biggest image model on this page and the most permissively licensed - Apache-2.0 on a 20B "
    "generator is unusual, and it is why this stays worth listing despite being the oldest of the "
    "current set. What you buy for the size is prompt understanding and world knowledge: it follows "
    "long, compositional prompts that the distilled 4-to-8-step models drop parts of. It also edits, "
    "not just generates. What you pay is speed - it is a base model at 30 steps, not a turbo, so it "
    "is the slowest option here by a wide margin. Reach for it when a prompt keeps coming out wrong "
    "elsewhere, not as a default."
)

SOURCES = [('Model card', 'https://huggingface.co/Qwen/Qwen-Image'),
           ('mflux support', 'https://github.com/filipstrand/mflux/blob/main/src/mflux/models/qwen/README.md')]

SCORES = {'agentic': [], 'coding': []}

# Which engine the card opens on and the glance row names.
BEST_ENGINE = 'mflux'

# Repositories tracker/measure.py harvests for this model.
QUANT_SOURCES = {'mlx': ['Qwen/Qwen-Image']}

# Measured by tracker/measure.py - do not hand-edit. gb is summed repo bytes;
# bpw is gb*8/PARAMS_B and is omitted for pruned or native-precision builds.
LADDER = {'mlx': [{'label': 'Qwen-Image',
          'repo': 'Qwen/Qwen-Image',
          'gb': 57.7,
          'kind': 'native',
          'bpw': None}]}

# Bytes of KV per token at fp16, the context ceiling, and how it was derived.
# None for models with no growing cache (diffusion, TTS).
KV = {'bytes_per_token': None, 'max_context': None, 'derivation': ''}

# Per-engine status. Keys must be engines whose modality matches MODALITY.
ENGINES = {
    'mflux': {'status': 'degraded', 'label': 'Runs, slow',
              'note': "Supported including its edit mode, and ungated. mflux flags it plainly as "
                      "the large, slower option: 30 steps against 4 to 8 for the distilled models, "
                      "on 20B of weights. Quantise to q8 unless you have the memory to spare.",
              'issues': []},
    'mlxvideo': {'status': 'blocked', 'label': 'Blocked',
                 'note': "MLX-Video's image support covers the FLUX line, not this.",
                 'issues': []},
    'diffusionkit': {'status': 'blocked', 'label': 'Predates it',
                     'note': "DiffusionKit implements Stable Diffusion 3 and FLUX.1 only.",
                     'issues': []},
}
