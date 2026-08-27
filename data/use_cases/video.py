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

AXIS = ('One realistic option today. Video is where Apple Silicon is furthest behind - expect minutes '
 'per clip.')

# Curated ordering, best first. Each entry is (model_id, metric_name, value).
# Membership is editorial; see AGENTS.md before reordering.
RANK = [['ltx2', 'text/image-to-video with synced audio', 'fp8 build fits']]
