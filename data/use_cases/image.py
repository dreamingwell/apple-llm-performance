"""Image generation - use case record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'image'
# Position in the What-for? dropdown. Explicit so a new category cannot
# reshuffle the menu; gaps of 10 make insertion cheap.
DISPLAY_ORDER = 70
LABEL = 'Image generation'
MODALITY = 'image'
FIDELITY_GATE = 'mild'

AXIS = ('No shared benchmark exists for these the way SWE-bench exists for coding, so this order is '
 'editorial: what the maintained runtime recommends, weighed against licence and footprint.')

# Curated ordering, best first. Each entry is (model_id, metric_name, value).
# Membership is editorial; see AGENTS.md before reordering.
RANK = [['zimage', 'Apache-2.0, fast, strong realism', "mflux's own lead recommendation"],
 ['flux2k4', '4B, edits as well as it generates', 'smallest good option'],
 ['flux2k9', '9B, better adherence', 'bf16 only']]
