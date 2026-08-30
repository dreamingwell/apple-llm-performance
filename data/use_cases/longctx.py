"""Long context - use case record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'longctx'
# Position in the What-for? dropdown. Explicit so a new category cannot
# reshuffle the menu; gaps of 10 make insertion cheap.
DISPLAY_ORDER = 60
LABEL = 'Long context'
MODALITY = 'text'
FIDELITY_GATE = 'mild'

AXIS = ('Ranked by KV bytes per token against the advertised ceiling - the models with a 1M window '
 'and latent attention are the only ones where a long context is affordable.')

# Curated ordering, best first. Each entry is (model_id, metric_name, value).
# Membership is editorial; see AGENTS.md before reordering.
RANK = [['glm53f', '1M ctx at 11 KiB/token', '12 GB full, oMLX only'],
 ['kimik3', '1M ctx at 27 KiB/token', '29 GB full'],
 ['v4flash', '1M ctx at 48 KiB/token', '52 GB full'],
 ['v4pro', '1M ctx at 69 KiB/token', '74 GB full'],
 ['glm52', '1M ctx at 88 KiB/token', '94 GB full'],
 ['m3', '1M ctx at 120 KiB/token', '129 GB full'],
 ['qcnext', '262k ctx at 24 KiB/token', '6 GB full'],
 ['q38fnext', '262k ctx at 24 KiB/token', '6 GB full'],
 ['qwen38', '262k ctx at 64 KiB/token', '17 GB full'],
 ['glm47f', '203k ctx at 53 KiB/token', '11 GB full'],
 ['gemma4', '262k ctx at 160 KiB/token', '43 GB full']]
