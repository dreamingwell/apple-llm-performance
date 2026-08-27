"""mflux - engine record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'mflux'
NAME = 'mflux'
# Tab position on every card. Explicit so adding an engine cannot silently
# reshuffle the others; leave gaps of 10 to make insertion cheap.
DISPLAY_ORDER = 90
MODALITIES = ['image']
FORMAT = 'MLX'
INTERFACE = 'CLI + Python API'
API = 'none - library and CLI'
LICENSE = 'MIT'
REPO = 'filipstrand/mflux'

RELEASE_FEED = None

WHAT = ('A line-by-line MLX port of a dozen image model families, written from scratch rather than '
 'wrapping diffusers - FLUX.2, Z-Image, Qwen Image, Krea 2, Ideogram 4, FIBO and more, plus '
 'SeedVR2 for upscaling and Depth Pro for depth. It is deliberately minimal and explicit, and '
 'it is the most active image runtime on Apple Silicon by a distance. There is no server: you '
 'drive it from the CLI or import it, so putting it behind an API is your job.')

# Issues that affect every model on this engine.
CROSS_ISSUES = []

# Quant family this engine loads.
QUANT_FAMILY = 'mlx'
