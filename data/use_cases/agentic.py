"""Agentic & tool use - use case record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'agentic'
# Position in the What-for? dropdown. Explicit so a new category cannot
# reshuffle the menu; gaps of 10 make insertion cheap.
DISPLAY_ORDER = 10
LABEL = 'Agentic & tool use'
MODALITY = 'text'
FIDELITY_GATE = 'mild'

AXIS = ('Tool-use and agent benchmarks. Scores are from different suites - they justify each '
 'placement rather than being directly comparable.')

# Curated ordering, best first. Each entry is (model_id, metric_name, value).
# Membership is editorial; see AGENTS.md before reordering.
RANK = [['kimik3', 'MCPMark-Verified', '94.5'],
 ['qwenmax', 'Terminal-Bench 2.1', '86.6'],
 ['glm52', 'Terminal-Bench 2.1', '81.0'],
 ['q38fnext', 'CoWorkBench', '73.9'],
 ['gemma4', 'τ²-Bench', '86.4'],
 ['qwen38', 'Terminal-Bench 2.1', '73.0'],
 ['glimmer', 'MCP Atlas', '75.5'],
 ['m3', 'MCP Atlas', '74.2'],
 ['qcnext', 'Terminal-Bench 2.0', '36.2'],
 ['glm47f', 'τ²-Bench', '79.5'],
 ['gptoss', 'τ-Bench Retail', '67.8'],
 ['v4pro', 'GDPval-AA', '1554'],
 ['v4flash', 'GDPval-AA max effort', '1388']]
