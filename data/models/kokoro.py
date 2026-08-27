"""Kokoro 82M - model record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'kokoro'
MODALITY = 'audio'
NAME = 'Kokoro 82M'
ARCH = '82M text-to-speech'
LICENSE = 'Apache-2.0'
CONTEXT = 'EN, JA, ZH, FR, ES, IT, PT, HI'
CONTEXT_LABEL = 'Coverage'
HF = 'hexgrad/Kokoro-82M'
PARAMS_B = 0.082

NOTE = ('The default answer for narration on a Mac, and by download count the most used open TTS '
 'model there is. 82M parameters, Apache-2.0, four MLX precisions published, and small enough '
 'that the whole model is smaller than one layer of most things on this page.')

SOURCES = [('Model card', 'https://huggingface.co/hexgrad/Kokoro-82M'),
 ('MLX builds', 'https://huggingface.co/mlx-community/Kokoro-82M-bf16')]

SCORES = {'agentic': [], 'coding': []}

# Which engine the card opens on and the glance row names.
BEST_ENGINE = 'mlxaudio'

# Repositories tracker/measure.py harvests for this model.
QUANT_SOURCES = {'mlx': ['mlx-community/Kokoro-82M-bf16',
         'mlx-community/Kokoro-82M-8bit',
         'mlx-community/Kokoro-82M-4bit']}

# Measured by tracker/measure.py - do not hand-edit. gb is summed repo bytes;
# bpw is gb*8/PARAMS_B and is omitted for pruned or native-precision builds.
LADDER = {'gguf': [],
 'mlx': [{'bpw': None,
          'gb': 0.36,
          'kind': 'native',
          'label': 'Kokoro-82M-bf16',
          'repo': 'mlx-community/Kokoro-82M-bf16'},
         {'bpw': None,
          'gb': 0.32,
          'kind': 'native',
          'label': 'Kokoro-82M-8bit',
          'repo': 'mlx-community/Kokoro-82M-8bit'},
         {'bpw': None,
          'gb': 0.31,
          'kind': 'native',
          'label': 'Kokoro-82M-4bit',
          'repo': 'mlx-community/Kokoro-82M-4bit'}]}

# Bytes of KV per token at fp16, the context ceiling, and how it was derived.
# None for models with no growing cache (diffusion, TTS).
KV = {'bytes_per_token': None, 'max_context': None, 'derivation': ''}

# Per-engine status. Keys must be engines whose modality matches MODALITY.
ENGINES = {'mlxaudio': {'status': 'works',
              'label': 'Best path',
              'note': "First in MLX-Audio's own table, four precisions published under "
                      'mlx-community, eight languages. For narration this is the default and '
                      'the burden of proof is on anything you would pick instead.',
              'issues': []}}
