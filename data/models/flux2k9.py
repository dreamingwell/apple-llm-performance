"""FLUX.2 Klein 9B - model record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'flux2k9'
MODALITY = 'image'
NAME = 'FLUX.2 Klein 9B'
ARCH = 'Rectified-flow DiT · 9B · distilled and base'
LICENSE = 'FLUX.2 (non-commercial for Klein)'
CONTEXT = 'up to ~4 MP, edit-capable'
CONTEXT_LABEL = 'Output'
HF = 'black-forest-labs/FLUX.2-klein-9B'
PARAMS_B = 9

NOTE = ('The larger Klein. Better prompt adherence and detail than the 4B at rather more than twice '
 'the footprint, and no quantised community builds published yet - so this is a '
 'bf16-or-nothing choice today.')

SOURCES = [('Model card', 'https://huggingface.co/black-forest-labs/FLUX.2-klein-9B')]

SCORES = {'agentic': [], 'coding': []}

# Which engine the card opens on and the glance row names.
BEST_ENGINE = 'mflux'

# Repositories tracker/measure.py harvests for this model.
QUANT_SOURCES = {'mlx': ['black-forest-labs/FLUX.2-klein-9B']}

# Measured by tracker/measure.py - do not hand-edit. gb is summed repo bytes;
# bpw is gb*8/PARAMS_B and is omitted for pruned or native-precision builds.
LADDER = {'gguf': [],
 'mlx': [{'bpw': None,
          'gb': 52.86,
          'kind': 'native',
          'label': 'FLUX.2-klein-9B',
          'repo': 'black-forest-labs/FLUX.2-klein-9B'}]}

# Bytes of KV per token at fp16, the context ceiling, and how it was derived.
# None for models with no growing cache (diffusion, TTS).
KV = {'bytes_per_token': None, 'max_context': None, 'derivation': ''}

# Per-engine status. Keys must be engines whose modality matches MODALITY.
ENGINES = {'mflux': {'status': 'works',
           'label': 'Runs',
           'note': 'Same native FLUX.2 implementation as the 4B, just larger. No quantised '
                   'builds published, so plan for the full 52.9 GB.',
           'issues': []},
 'mlxvideo': {'status': 'degraded',
              'label': 'Possible, unverified',
              'note': "Not called out in the project's model list.",
              'issues': []},
 'diffusionkit': {'status': 'blocked',
                  'label': 'Predates it',
                  'note': 'Unmaintained since April 2025.',
                  'issues': []}}
