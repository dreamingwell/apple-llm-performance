"""Voice agents (speech-to-speech) - use case record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'voice'
# Position in the What-for? dropdown. Explicit so a new category cannot
# reshuffle the menu; gaps of 10 make insertion cheap.
DISPLAY_ORDER = 90
LABEL = 'Voice agents (speech-to-speech)'
MODALITY = 'audio'
FIDELITY_GATE = 'mild'

AXIS = ('End-to-end speech models, where the model hears and speaks directly rather than being wired '
 'between an ASR and a TTS.')

# Curated ordering, best first. Each entry is (model_id, metric_name, value).
# Membership is editorial; see AGENTS.md before reordering.
RANK = [['voicechat', 'full-duplex, tools mid-turn', '~450 ms']]
