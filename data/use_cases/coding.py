"""Coding - use case record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'coding'
# Position in the What-for? dropdown. Explicit so a new category cannot
# reshuffle the menu; gaps of 10 make insertion cheap.
DISPLAY_ORDER = 20
LABEL = 'Coding'
MODALITY = 'text'
FIDELITY_GATE = 'mild'

AXIS = ('Ordered on SWE-bench Verified where published, since it is the one coding benchmark most of '
 'these models report.')

# Curated ordering, best first. Each entry is (model_id, metric_name, value).
# Membership is editorial; see AGENTS.md before reordering.
RANK = [['v4pro', 'SWE-bench Verified', '80.6%'],
 ['m3', 'SWE-bench Verified', '80.5%'],
 ['qwenmax', 'SWE-bench Pro', '67.7'],
 ['ornith15', 'SWE-bench Verified', '79.0'],
 ['glimmer', 'SWE-bench Verified', '76.0'],
 ['qcnext', 'SWE-bench Verified', '74.2%'],
 ['gptoss', 'SWE-bench Verified', '62.4%'],
 ['q38fnext', 'SWE-bench Pro', '62.5'],
 ['glm52', 'SWE-bench Pro', '62.1%'],
 ['qwen38', 'SWE-bench Pro', '61.7'],
 ['glm47f', 'SWE-bench Verified', '59.2%'],
 ['gemma4', 'SWE-bench Verified', '52.0%'],
 ['nemolight', 'SWE-bench Verified', '51.56'],
 ['kimik3', 'LiveBench Coding', '81.45']]
