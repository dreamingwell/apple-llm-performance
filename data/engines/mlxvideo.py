"""MLX-Video - engine record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'mlxvideo'
NAME = 'MLX-Video'
# Tab position on every card. Explicit so adding an engine cannot silently
# reshuffle the others; leave gaps of 10 to make insertion cheap.
DISPLAY_ORDER = 110
MODALITIES = ['video', 'image']
FORMAT = 'MLX'
INTERFACE = 'CLI + Python API'
API = 'none - library and CLI'
LICENSE = 'MIT'
REPO = 'Blaizzy/mlx-video'

# Canonical website, linked wherever this engine is named in prose.
SITE = 'https://github.com/Blaizzy/mlx-video'

# The names this engine actually goes by in the notes. Bare 'vLLM' is
# deliberately not an alias anywhere: it means upstream vLLM, not the plugin.
PROSE_ALIASES = ['MLX-Video']

RELEASE_FEED = None

WHAT = ('Inference and finetuning for image, video and audio generation models. Same author as '
 'MLX-Audio. Worth checking the commit history before planning around it - it moves in bursts '
 'rather than continuously.')

# Issues that affect every model on this engine.
CROSS_ISSUES = []

# Quant family this engine loads.
QUANT_FAMILY = 'mlx'
