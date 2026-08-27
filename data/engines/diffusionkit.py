"""DiffusionKit - engine record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'diffusionkit'
NAME = 'DiffusionKit'
# Tab position on every card. Explicit so adding an engine cannot silently
# reshuffle the others; leave gaps of 10 to make insertion cheap.
DISPLAY_ORDER = 120
MODALITIES = ['image']
FORMAT = 'MLX + Core ML'
INTERFACE = 'CLI + Python API'
API = 'none - library and CLI'
LICENSE = 'MIT'
REPO = 'argmaxinc/DiffusionKit'

RELEASE_FEED = None

WHAT = ("Argmax's on-device image generation for Apple Silicon, covering both MLX and Core ML. Solid "
 'engineering, but it has not been touched since April 2025, so it predates every model added '
 'to this page and should be treated as a reference implementation rather than a live option.')

# Issues that affect every model on this engine.
CROSS_ISSUES = []

# Quant family this engine loads.
QUANT_FAMILY = 'mlx'
