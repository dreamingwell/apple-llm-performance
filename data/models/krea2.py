"""Krea 2 Turbo - model record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'krea2'
MODALITY = 'image'
NAME = 'Krea 2 Turbo'
ARCH = '12B DiT, DMD-distilled to 8 steps'
LICENSE = 'Krea 2 community licence (gated)'
CONTEXT = '1024x1024 typical, 8 steps'
CONTEXT_LABEL = 'Output'
HF = 'krea/Krea-2-Turbo'
PARAMS_B = 12

NOTE = (
    "Released June 2026 and the newest general-purpose image model mflux carries. Its own "
    "description is the useful one: very good quality across a wide range of styles, which makes it "
    "the creative-exploration option rather than the photorealism one. Distilled to 8 steps, so it "
    "is quick despite being 12B. The full-precision download is 62 GB, which is the number that "
    "decides whether it fits - quantise to q8 and it comes down sharply. There is a companion "
    "`Krea-2-Raw` on the hub with marginally more downloads; Turbo is the one mflux drives. Weights "
    "are gated, and the licence is a community licence rather than open weights."
)

SOURCES = [('Model card', 'https://huggingface.co/krea/Krea-2-Turbo'),
           ('mflux support', 'https://github.com/filipstrand/mflux/blob/main/src/mflux/models/krea2/README.md'),
           ('LoRA collection', 'https://huggingface.co/collections/krea/krea-2-loras')]

SCORES = {'agentic': [], 'coding': []}

# Which engine the card opens on and the glance row names.
BEST_ENGINE = 'mflux'

# Repositories tracker/measure.py harvests for this model.
QUANT_SOURCES = {'mlx': ['krea/Krea-2-Turbo']}

# Measured by tracker/measure.py - do not hand-edit. gb is summed repo bytes;
# bpw is gb*8/PARAMS_B and is omitted for pruned or native-precision builds.
LADDER = {'mlx': [{'label': 'Krea-2-Turbo',
          'repo': 'krea/Krea-2-Turbo',
          'gb': 61.95,
          'kind': 'native',
          'bpw': None}]}

# Bytes of KV per token at fp16, the context ceiling, and how it was derived.
# None for models with no growing cache (diffusion, TTS).
KV = {'bytes_per_token': None, 'max_context': None, 'derivation': ''}

# Per-engine status. Keys must be engines whose modality matches MODALITY.
ENGINES = {
    'mflux': {'status': 'works', 'label': 'Runs',
              'note': "First-class in mflux, with img2img, LoRA and quantisation all supported. "
                      "Defaults to 8 steps at q8. `mflux-generate --model krea2` and the weights "
                      "pull automatically once you have accepted the gate.",
              'issues': []},
    'mlxvideo': {'status': 'blocked', 'label': 'Blocked',
                 'note': "MLX-Video's image support covers the FLUX line, not this.",
                 'issues': []},
    'diffusionkit': {'status': 'blocked', 'label': 'Predates it',
                     'note': "DiffusionKit implements Stable Diffusion 3 and FLUX.1. It has not "
                             "been extended to the 2026 model generation.",
                     'issues': []},
}
