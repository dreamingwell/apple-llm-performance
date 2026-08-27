"""MLX-Audio - engine record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'mlxaudio'
NAME = 'MLX-Audio'
# Tab position on every card. Explicit so adding an engine cannot silently
# reshuffle the others; leave gaps of 10 to make insertion cheap.
DISPLAY_ORDER = 100
MODALITIES = ['audio']
FORMAT = 'MLX'
INTERFACE = 'CLI + Python API + web UI'
API = 'local web interface'
LICENSE = 'MIT'
REPO = 'Blaizzy/mlx-audio'

# Canonical website, linked wherever this engine is named in prose.
SITE = 'https://github.com/Blaizzy/mlx-audio'

# The names this engine actually goes by in the notes. Bare 'vLLM' is
# deliberately not an alias anywhere: it means upstream vLLM, not the plugin.
PROSE_ALIASES = ['MLX-Audio']

RELEASE_FEED = None

WHAT = ('The centre of gravity for audio on Apple Silicon, and the largest catalogue on this page: '
 'twenty-odd TTS families, a similar spread of speech-to-text, speaker diarisation, speech '
 'enhancement and music generation. If an audio model has an MLX port at all, this is usually '
 'where it lives.')

# Issues that affect every model on this engine.
CROSS_ISSUES = []

# Quant family this engine loads.
QUANT_FAMILY = 'mlx'
