"""LTX-2.3 - model record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'ltx2'
MODALITY = 'video'
NAME = 'LTX-2.3'
ARCH = 'Video DiT with synchronised audio'
LICENSE = 'LTX open weights'
CONTEXT = 'text-to-video and image-to-video, with audio'
CONTEXT_LABEL = 'Output'
HF = 'Lightricks/LTX-2.3'
PARAMS_B = 19

NOTE = ("Lightricks' video model, and the one generating video with synchronised audio rather than "
 'silent clips. The fp8 build at 58.7 GB is the one that fits a real machine; the full release '
 'is 156 GB. Video is where Apple Silicon is furthest behind - expect minutes per clip, not '
 "seconds, and check MLX-Video's commit history before planning around it.")

SOURCES = [('Model card', 'https://huggingface.co/Lightricks/LTX-2.3')]

SCORES = {'agentic': [], 'coding': []}

# Which engine the card opens on and the glance row names.
BEST_ENGINE = 'mlxvideo'

# Repositories tracker/measure.py harvests for this model.
QUANT_SOURCES = {'mlx': ['Lightricks/LTX-2.3', 'Lightricks/LTX-2.3-fp8']}

# Measured by tracker/measure.py - do not hand-edit. gb is summed repo bytes;
# bpw is gb*8/PARAMS_B and is omitted for pruned or native-precision builds.
LADDER = {'gguf': [],
 'mlx': [{'bpw': None,
          'gb': 156.01,
          'kind': 'native',
          'label': 'LTX-2.3',
          'repo': 'Lightricks/LTX-2.3'},
         {'bpw': None,
          'gb': 58.68,
          'kind': 'native',
          'label': 'LTX-2.3-fp8',
          'repo': 'Lightricks/LTX-2.3-fp8'}]}

# Bytes of KV per token at fp16, the context ceiling, and how it was derived.
# None for models with no growing cache (diffusion, TTS).
KV = {'bytes_per_token': None, 'max_context': None, 'derivation': ''}

# Per-engine status. Keys must be engines whose modality matches MODALITY.
ENGINES = {'mlxvideo': {'status': 'degraded',
              'label': 'Runs, slow',
              'note': 'The MLX route to text-to-video and image-to-video with synchronised '
                      'audio. Two caveats worth stating plainly: video generation on Apple '
                      "Silicon is minutes per clip rather than seconds, and MLX-Video's last "
                      'push was several months before the models on this page - check it still '
                      'tracks the checkpoint you want before committing.',
              'issues': []}}
