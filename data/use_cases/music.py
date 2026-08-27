"""Music generation - use case record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'music'
# Position in the What-for? dropdown. Explicit so a new category cannot
# reshuffle the menu; gaps of 10 make insertion cheap.
DISPLAY_ORDER = 110
LABEL = 'Music generation'
MODALITY = 'audio'
FIDELITY_GATE = 'mild'

AXIS = 'Song generation from lyrics. One maintained MLX path.'

# Curated ordering, best first. Each entry is (model_id, metric_name, value).
# Membership is editorial; see AGENTS.md before reordering.
RANK = [['mmmusic3', 'lyrics in, 44.1 kHz stereo out', '7 precisions']]
