"""Many parallel streams - use case record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'concurrency'
# Position in the What-for? dropdown. Explicit so a new category cannot
# reshuffle the menu; gaps of 10 make insertion cheap.
DISPLAY_ORDER = 50
LABEL = 'Many parallel streams'
MODALITY = 'text'
FIDELITY_GATE = 'mild'

AXIS = ('Ranked by active parameters and KV cost per token, because at concurrency those decide '
 'throughput far more than the benchmark scores do.')

# Curated ordering, best first. Each entry is (model_id, metric_name, value).
# Membership is editorial; see AGENTS.md before reordering.
RANK = [['qcnext', '3B active, 24 KiB/token', 'cheapest overall'],
 ['q38fnext', '6B active, 24 KiB/token', 'cheap but blocked'],
 ['glm47f', '3B active, 53 KiB/token', 'cheapest'],
 ['nemolight', '3B active, 6 KiB/token', 'cheapest KV'],
 ['gptoss', '5.1B active, 36 KiB/token', 'strong'],
 ['glimmer', 'dense 30B, 13 KiB/token', 'cheap KV'],
 ['qwen38', 'dense 27.8B, 64 KiB/token', 'good'],
 ['v4flash', '13B active, 48 KiB/token', 'large but cheap'],
 ['m3', '23B active, 120 KiB/token', 'expensive KV'],
 ['glm47', '32B active, 368 KiB/token', 'KV-bound']]
