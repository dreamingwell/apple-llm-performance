"""Tracked issues in lmstudio-ai/lmstudio-bug-tracker.

One record, one file. See AGENTS.md for the schema and the rules.
"""

REPO = 'lmstudio-ai/lmstudio-bug-tracker'

# number -> severity / headline / why it matters.
ISSUES = {2240: {'severity': 'medium',
        'headline': 'Too much memory allocated',
        'why': 'Over-allocation relative to the model. On a 256 GB machine running a 200 GB '
               'model there is no slack to absorb it.'},
 2243: {'severity': 'low',
        'headline': 'Native MLX tool calling: parser coverage requests',
        'why': 'Tool-call parsing is per-family, so a model whose format has no parser returns '
               'its calls as text. Track this if your model is not in the supported list.'},
 2265: {'severity': 'high',
        'headline': 'MLX Gemma 4 silently ignores attached images and confabulates a '
                    'description',
        'why': 'The GGUF build of the same model handles them. A vision model that invents '
               'what it cannot see is the worst available failure mode, and it is '
               'engine-specific.'},
 2273: {'severity': 'high',
        'headline': 'MLX quants shown as having no tool use when they do',
        'why': 'The capability badge is wrong, so the app steers you away from working '
               'tool-calling builds. Cosmetic in code, decision-changing in practice.'},
 2323: {'severity': 'critical',
        'headline': 'MLX engine silently clamps context to 4864 tokens, ignoring all overrides',
        'why': 'Filed against a hybrid linear-attention model - the Qwen3.8 shape. A silent '
               '4864-token ceiling makes any agent workload fail in a way that looks like the '
               'model being stupid rather than the engine being misconfigured.'},
 2324: {'severity': 'low',
        'headline': "Catalog entries show 'Invalid Key ID' with no download options",
        'why': 'A catalogue-side failure rather than an inference one, but the catalogue is '
               'how most people get models into this app.'}}
