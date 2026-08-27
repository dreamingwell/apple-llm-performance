"""LTX-2.5 - model record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'ltx25'
MODALITY = 'video'
NAME = 'LTX-2.5'
ARCH = '22B video DiT + 12B text encoder, with synchronised audio'
LICENSE = 'LTX-2.x Community License (non-commercial above $10M revenue)'
CONTEXT = 'text-to-video and image-to-video, with audio'
CONTEXT_LABEL = 'Output'
HF = 'Lightricks/LTX-2.5'
PARAMS_B = 34

NOTE = (
    "The current Lightricks video model, released 2026-07-23, and already the more downloaded of "
    "the two. It supersedes LTX-2.3 on quality - but not on this page, because the engine here "
    "cannot load it yet. MLX weights do exist: `mlx-community/ltx-2.5-mlx` and an 8-bit build at "
    "23.9 GB. What drives them is a community port, `xocialize/ltx-2-mlx`, on an `ltx-2.5` branch "
    "with no stars and no releases, so it is not carried as an engine here. Its own card quotes 62.4 "
    "GB peak on a 128 GB machine, reducible to 40.7 GB by evicting components between stages. Note "
    "the licence is not open weights in the usual sense: it is a community licence that requires a "
    "paid agreement above $10M of revenue, and the repository is gated. **LTX-2.3 remains the "
    "version this page can actually run** - see its card."
)

SOURCES = [('Model card', 'https://huggingface.co/Lightricks/LTX-2.5'),
           ('MLX conversion', 'https://huggingface.co/mlx-community/ltx-2.5-mlx'),
           ('Community MLX port', 'https://github.com/xocialize/ltx-2-mlx'),
           ('MLX-Video support request', 'https://github.com/Blaizzy/mlx-video/issues/51')]

SCORES = {'agentic': [], 'coding': []}

# Which engine the card opens on and the glance row names.
BEST_ENGINE = 'mlxvideo'

# Repositories tracker/measure.py harvests for this model.
QUANT_SOURCES = {'mlx': ['mlx-community/ltx-2.5-mlx',
                         'mlx-community/ltx-2.5-mlx-q8',
                         'mlx-community/ltx-2.5-mlx-ditq8']}

# Measured by tracker/measure.py - do not hand-edit. gb is summed repo bytes;
# bpw is gb*8/PARAMS_B and is omitted for pruned or native-precision builds.
LADDER = {'mlx': [{'label': 'ltx-2.5-mlx',
          'repo': 'mlx-community/ltx-2.5-mlx',
          'gb': 110.04,
          'kind': 'native',
          'bpw': None},
         {'label': 'ltx-2.5-mlx-q8',
          'repo': 'mlx-community/ltx-2.5-mlx-q8',
          'gb': 23.85,
          'kind': 'native',
          'bpw': None},
         {'label': 'ltx-2.5-mlx-ditq8',
          'repo': 'mlx-community/ltx-2.5-mlx-ditq8',
          'gb': 20.6,
          'kind': 'native',
          'bpw': None}]}

# Bytes of KV per token at fp16, the context ceiling, and how it was derived.
# None for models with no growing cache (diffusion, TTS).
KV = {'bytes_per_token': None, 'max_context': None, 'derivation': ''}

# Per-engine status. Keys must be engines whose modality matches MODALITY.
ENGINES = {
    'mlxvideo': {'status': 'blocked', 'label': 'Blocked',
                 'note': "MLX-Video implements LTX-2 and LTX-2.3 only; its README names no 2.5 "
                         "pipeline and its pre-converted weights stop at 2.3. Support was requested "
                         "on 2026-08-19 and is unanswered, and the project's last commit predates "
                         "LTX-2.5 by more than two months. Converted MLX weights exist on the hub "
                         "regardless, driven by a separate community port rather than this engine.",
                 'issues': ['Blaizzy/mlx-video#51']},
}
