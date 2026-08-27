"""Tracked issues in Blaizzy/mlx-video.

One record, one file. See AGENTS.md for the schema and the rules.
"""

REPO = 'Blaizzy/mlx-video'

# number -> severity / headline / why it matters.
ISSUES = {51: {'severity': 'high',
               'headline': 'Add support for LTX-2.5',
               'why': 'LTX-2.5 is the current Lightricks video model and MLX weights for it are '
                      'already published, but mlx-video only implements LTX-2 and LTX-2.3. Until '
                      'this lands, the newest weights have no loader in this engine.'}}
