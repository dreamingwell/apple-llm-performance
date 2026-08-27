"""MiniMax Music 3 - model record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'mmmusic3'
MODALITY = 'audio'
NAME = 'MiniMax Music 3'
ARCH = 'Hierarchical AR + flow matching · song generation'
LICENSE = 'MiniMax open weights'
CONTEXT = 'lyrics in, 44.1 kHz stereo out'
CONTEXT_LABEL = 'Output'
HF = 'MiniMaxAI/MiniMax-Music-3'
PARAMS_B = 7

NOTE = ('The only full song-generation model with a maintained MLX port: lyrics in, 44.1 kHz stereo '
 'out, via a hierarchical autoregressive stage feeding flow matching. Seven MLX precisions '
 'published, from bf16 at 28.5 GB down to 4-bit at 9.2 GB.')

SOURCES = [('MLX builds', 'https://huggingface.co/mlx-community/MiniMax-Music3-bf16'),
 ('MLX-Audio music guide', 'https://github.com/Blaizzy/mlx-audio')]

SCORES = {'agentic': [], 'coding': []}

# Which engine the card opens on and the glance row names.
BEST_ENGINE = 'mlxaudio'

# Repositories tracker/measure.py harvests for this model.
QUANT_SOURCES = {'mlx': ['mlx-community/MiniMax-Music3-bf16',
         'mlx-community/MiniMax-Music3-8bit',
         'mlx-community/MiniMax-Music3-4bit']}

# Measured by tracker/measure.py - do not hand-edit. gb is summed repo bytes;
# bpw is gb*8/PARAMS_B and is omitted for pruned or native-precision builds.
LADDER = {'gguf': [],
 'mlx': [{'bpw': None,
          'gb': 28.51,
          'kind': 'native',
          'label': 'MiniMax-Music3-bf16',
          'repo': 'mlx-community/MiniMax-Music3-bf16'},
         {'bpw': None,
          'gb': 14.17,
          'kind': 'native',
          'label': 'MiniMax-Music3-8bit',
          'repo': 'mlx-community/MiniMax-Music3-8bit'},
         {'bpw': None,
          'gb': 9.2,
          'kind': 'native',
          'label': 'MiniMax-Music3-4bit',
          'repo': 'mlx-community/MiniMax-Music3-4bit'}]}

# Bytes of KV per token at fp16, the context ceiling, and how it was derived.
# None for models with no growing cache (diffusion, TTS).
KV = {'bytes_per_token': None, 'max_context': None, 'derivation': ''}

# Per-engine status. Keys must be engines whose modality matches MODALITY.
ENGINES = {'mlxaudio': {'status': 'works',
              'label': 'Best path',
              'note': 'Seven precisions published, from bf16 at 28.5 GB to 4-bit at 9.2 GB, '
                      'plus MXFP4/MXFP8/NVFP4. The only maintained MLX path to full song '
                      'generation with lyrics.',
              'issues': []}}
