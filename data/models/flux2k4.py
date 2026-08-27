"""FLUX.2 Klein 4B - model record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'flux2k4'
MODALITY = 'image'
NAME = 'FLUX.2 Klein 4B'
ARCH = 'Rectified-flow DiT · 4B · distilled and base'
LICENSE = 'FLUX.2 (non-commercial for Klein)'
CONTEXT = 'up to ~4 MP, edit-capable'
CONTEXT_LABEL = 'Output'
HF = 'black-forest-labs/FLUX.2-klein-4B'
PARAMS_B = 4

NOTE = ('The pragmatic default for image generation on a Mac. 4B is small enough that the whole thing '
 'sits in a few gigabytes, it edits as well as it generates, and mflux implements it natively. '
 'Apple quotes FLUX-dev-4bit as 3.8x faster on M5 than M4, which is the largest '
 'generation-over-generation jump of anything on this page.')

SOURCES = [('Model card', 'https://huggingface.co/black-forest-labs/FLUX.2-klein-4B'),
 ('mflux FLUX.2 guide',
  'https://github.com/filipstrand/mflux/blob/main/src/mflux/models/flux2/README.md')]

SCORES = {'agentic': [], 'coding': []}

# Which engine the card opens on and the glance row names.
BEST_ENGINE = 'mflux'

# Repositories tracker/measure.py harvests for this model.
QUANT_SOURCES = {'gguf': ['unsloth/FLUX.2-klein-4B-GGUF'], 'mlx': ['black-forest-labs/FLUX.2-klein-4B']}

# Measured by tracker/measure.py - do not hand-edit. gb is summed repo bytes;
# bpw is gb*8/PARAMS_B and is omitted for pruned or native-precision builds.
LADDER = {'gguf': [{'bpw': None,
           'gb': 7.8,
           'kind': 'native',
           'label': 'flux-2-klein-4b-BF16',
           'repo': 'unsloth/FLUX.2-klein-4B-GGUF'},
          {'bpw': None,
           'gb': 4.3,
           'kind': 'native',
           'label': 'flux-2-klein-4b-Q8_0',
           'repo': 'unsloth/FLUX.2-klein-4B-GGUF'},
          {'bpw': None,
           'gb': 3.4,
           'kind': 'native',
           'label': 'flux-2-klein-4b-Q6_K',
           'repo': 'unsloth/FLUX.2-klein-4B-GGUF'},
          {'bpw': None,
           'gb': 3.1,
           'kind': 'native',
           'label': 'flux-2-klein-4b-Q5_K_M',
           'repo': 'unsloth/FLUX.2-klein-4B-GGUF'},
          {'bpw': None,
           'gb': 2.9,
           'kind': 'native',
           'label': 'flux-2-klein-4b-Q5_0',
           'repo': 'unsloth/FLUX.2-klein-4B-GGUF'},
          {'bpw': None,
           'gb': 2.7,
           'kind': 'native',
           'label': 'flux-2-klein-4b-Q4_1',
           'repo': 'unsloth/FLUX.2-klein-4B-GGUF'},
          {'bpw': None,
           'gb': 2.5,
           'kind': 'native',
           'label': 'flux-2-klein-4b-Q4_0',
           'repo': 'unsloth/FLUX.2-klein-4B-GGUF'},
          {'bpw': None,
           'gb': 2.1,
           'kind': 'native',
           'label': 'flux-2-klein-4b-Q3_K_M',
           'repo': 'unsloth/FLUX.2-klein-4B-GGUF'},
          {'bpw': None,
           'gb': 1.8,
           'kind': 'native',
           'label': 'flux-2-klein-4b-Q2_K',
           'repo': 'unsloth/FLUX.2-klein-4B-GGUF'}],
 'mlx': [{'bpw': None,
          'gb': 23.72,
          'kind': 'native',
          'label': 'FLUX.2-klein-4B',
          'repo': 'black-forest-labs/FLUX.2-klein-4B'}]}

# Bytes of KV per token at fp16, the context ceiling, and how it was derived.
# None for models with no growing cache (diffusion, TTS).
KV = {'bytes_per_token': None, 'max_context': None, 'derivation': ''}

# Per-engine status. Keys must be engines whose modality matches MODALITY.
ENGINES = {'mflux': {'status': 'works',
           'label': 'Runs',
           'note': 'mflux implements FLUX.2 natively - not a diffusers wrapper - and treats it '
                   'as the fastest and smallest family it carries, with edit capability. '
                   '`mflux-generate` and you are going. GGUF builds down to Q5 exist if 7.8 GB '
                   'of bf16 is more than you want to hold.',
           'issues': []},
 'mlxvideo': {'status': 'degraded',
              'label': 'Possible, unverified',
              'note': 'MLX-Video covers image models as well as video, but FLUX.2 is not '
                      'called out and the project moves in bursts. mflux is the maintained '
                      'path for this.',
              'issues': []},
 'diffusionkit': {'status': 'blocked',
                  'label': 'Predates it',
                  'note': 'DiffusionKit has not been updated since April 2025 and FLUX.2 '
                          'shipped in January 2026.',
                  'issues': []}}
