"""Video generation - use case record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'video'
# Position in the What-for? dropdown. Explicit so a new category cannot
# reshuffle the menu; gaps of 10 make insertion cheap.
DISPLAY_ORDER = 80
LABEL = 'Video generation'
MODALITY = 'video'
FIDELITY_GATE = 'mild'

AXIS = ('Three entries, one runnable, and that is the story. Video is where Apple silicon '
        'is furthest behind - expect minutes per clip. MiniMax-H3 is the one most people '
        'use and the only one whose 8-bit build fits a single Mac at 21.5 GB resident, and '
        'LTX-2.5 is the better-quality newer release; both have MLX weights driven by '
        'standalone ports rather than any engine tracked here. LTX-2.3 is what MLX-Video '
        'actually loads.')

# Curated ordering, best first. Each entry is (model_id, metric_name, value).
# Membership is editorial; see AGENTS.md before reordering.
RANK = [['ltx2', 'text/image-to-video with synced audio', 'the one MLX-Video loads'],
        ['mmh3', 'joint video+audio, 21.5 GB resident at 8-bit', 'no engine here loads it'],
        ['ltx25', 'newer and better than LTX-2.3', 'no engine here loads it']]
