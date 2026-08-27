"""Narration & text-to-speech - use case record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'narration'
# Position in the What-for? dropdown. Explicit so a new category cannot
# reshuffle the menu; gaps of 10 make insertion cheap.
DISPLAY_ORDER = 100
LABEL = 'Narration & text-to-speech'
MODALITY = 'audio'
FIDELITY_GATE = 'mild'

AXIS = ('Ordered on breadth of published MLX builds and language coverage; no common quality '
 'benchmark is published for these.')

# Curated ordering, best first. Each entry is (model_id, metric_name, value).
# Membership is editorial; see AGENTS.md before reordering.
RANK = [['kokoro', '8 languages, 4 MLX precisions', 'the default'],
 ['magpie', '9 languages, NVIDIA voice stack', 'community MLX build'],
 ['voicechat', 'speaks, but built for conversation', 'oversized for narration']]
