"""Terminal & CLI work - use case record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'terminal'
# Position in the What-for? dropdown. Explicit so a new category cannot
# reshuffle the menu; gaps of 10 make insertion cheap.
DISPLAY_ORDER = 30
LABEL = 'Terminal & CLI work'
MODALITY = 'text'
FIDELITY_GATE = 'mild'

AXIS = ('Terminal-Bench 2.1 only, so these are directly comparable. GLM-4.7 is excluded because its '
 '41.0 is on v2.0, a different benchmark.')

# Curated ordering, best first. Each entry is (model_id, metric_name, value).
# Membership is editorial; see AGENTS.md before reordering.
RANK = [['kimik3', 'Terminal-Bench 2.1', '88.3'],
 ['qwenmax', 'Terminal-Bench 2.1', '86.6'],
 ['glm52', 'Terminal-Bench 2.1', '81.0'],
 ['qwen38', 'Terminal-Bench 2.1', '73.0'],
 ['m3', 'Terminal-Bench 2.1', '66.0'],
 ['glimmer', 'Terminal-Bench 2.1', '51.7']]
