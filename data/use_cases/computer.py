"""Computer use (GUI) - use case record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'computer'
# Position in the What-for? dropdown. Explicit so a new category cannot
# reshuffle the menu; gaps of 10 make insertion cheap.
DISPLAY_ORDER = 40
LABEL = 'Computer use (GUI)'
MODALITY = 'text'
FIDELITY_GATE = 'mild'

AXIS = ('OSWorld and AndroidWorld, which are different suites - AndroidWorld figures are comparable '
 'to each other, OSWorld ones are not comparable to OSWorld-Verified. Only a handful of these '
 'models report computer-use numbers at all.')

# Curated ordering, best first. Each entry is (model_id, metric_name, value).
# Membership is editorial; see AGENTS.md before reordering.
RANK = [['kimik3', 'OSWorld-Verified', '84.8'],
 ['q38fnext', 'AndroidWorld', '84.5'],
 ['qwen38', 'AndroidWorld', '81.9'],
 ['glimmer', 'OSWorld-Verified', '65.9']]
