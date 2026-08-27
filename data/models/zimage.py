"""Z-Image Turbo 6B - model record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'zimage'
MODALITY = 'image'
NAME = 'Z-Image Turbo 6B'
ARCH = '6B DiT · distilled and base'
LICENSE = 'Apache-2.0'
CONTEXT = '1024×1024 typical'
CONTEXT_LABEL = 'Output'
HF = 'Tongyi-MAI/Z-Image-Turbo'
PARAMS_B = 6

NOTE = ('mflux leads its own README with this one, and describes it as fast, small and very good on '
 'realism. Apache-2.0, which separates it from the FLUX family for anything commercial. The '
 'published checkpoint is bf16, so the on-disk figure is larger than the parameter count '
 'suggests.')

SOURCES = [('mflux Z-Image guide',
  'https://github.com/filipstrand/mflux/blob/main/src/mflux/models/z_image/README.md')]

SCORES = {'agentic': [], 'coding': []}

# Which engine the card opens on and the glance row names.
BEST_ENGINE = 'mflux'

# Repositories tracker/measure.py harvests for this model.
QUANT_SOURCES = {'mlx': ['Tongyi-MAI/Z-Image-Turbo']}

# Measured by tracker/measure.py - do not hand-edit. gb is summed repo bytes;
# bpw is gb*8/PARAMS_B and is omitted for pruned or native-precision builds.
LADDER = {'gguf': [],
 'mlx': [{'bpw': None,
          'gb': 32.83,
          'kind': 'native',
          'label': 'Z-Image-Turbo',
          'repo': 'Tongyi-MAI/Z-Image-Turbo'}]}

# Bytes of KV per token at fp16, the context ceiling, and how it was derived.
# None for models with no growing cache (diffusion, TTS).
KV = {'bytes_per_token': None, 'max_context': None, 'derivation': ''}

# Per-engine status. Keys must be engines whose modality matches MODALITY.
ENGINES = {'mflux': {'status': 'works',
           'label': 'Best path',
           'note': 'The model mflux opens its own README with, described there as fast, small '
                   'and very good on realism, with both distilled and base variants and '
                   'training support. Apache-2.0 makes it the one to reach for if the FLUX '
                   'licence is a problem.',
           'issues': []},
 'mlxvideo': {'status': 'blocked',
              'label': 'Blocked',
              'note': "Not in the project's model list.",
              'issues': []},
 'diffusionkit': {'status': 'blocked',
                  'label': 'Predates it',
                  'note': 'Z-Image shipped in November 2025, after DiffusionKit stopped.',
                  'issues': []}}
