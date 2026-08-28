"""FIBO - model record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'fibo'
MODALITY = 'image'
NAME = 'FIBO'
ARCH = '8B DiT, JSON-native captions; Lite is a distilled 8-step variant'
LICENSE = 'Bria licence (gated); Fibo-lite is CC-BY-NC-4.0'
CONTEXT = '1024x1024 typical, 20-50 steps (8 for Lite)'
CONTEXT_LABEL = 'Output'
HF = 'briaai/FIBO'
PARAMS_B = 8

NOTE = (
    "The one with a clean provenance story: Bria trained it exclusively on licensed data, which is "
    "the differentiator rather than the pixels. If you are generating images for something "
    "commercial, that is a materially different risk position from every other model here, and it "
    "is the reason to accept a gated download. Technically it is JSON-native like Ideogram 4, built "
    "for long structured captions and professional-grade control. `Fibo-lite` is a distilled "
    "two-stage variant at roughly ten times the speed - 8 steps, no negative prompt - at some cost "
    "in quality, but note the Lite weights are CC-BY-NC-4.0, which undoes the commercial argument "
    "for using them."
)

SOURCES = [('Model card', 'https://huggingface.co/briaai/FIBO'),
           ('Fibo-lite', 'https://huggingface.co/briaai/Fibo-lite'),
           ('Technical paper', 'https://arxiv.org/abs/2511.06876'),
           ('mflux support', 'https://github.com/filipstrand/mflux/blob/main/src/mflux/models/fibo/README.md')]

SCORES = {'agentic': [], 'coding': []}

# Which engine the card opens on and the glance row names.
BEST_ENGINE = 'mflux'

# Repositories tracker/measure.py harvests for this model.
QUANT_SOURCES = {'mlx': ['briaai/FIBO', 'briaai/Fibo-lite']}

# Measured by tracker/measure.py - do not hand-edit. gb is summed repo bytes;
# bpw is gb*8/PARAMS_B and is omitted for pruned or native-precision builds.
LADDER = {'mlx': [{'label': 'FIBO', 'repo': 'briaai/FIBO', 'gb': 25.54, 'kind': 'native', 'bpw': None},
         {'label': 'Fibo-lite',
          'repo': 'briaai/Fibo-lite',
          'gb': 24.13,
          'kind': 'native',
          'bpw': None}]}

# Bytes of KV per token at fp16, the context ceiling, and how it was derived.
# None for models with no growing cache (diffusion, TTS).
KV = {'bytes_per_token': None, 'max_context': None, 'derivation': ''}

# Per-engine status. Keys must be engines whose modality matches MODALITY.
ENGINES = {
    'mflux': {'status': 'works', 'label': 'Runs',
              'note': "Both tiers are supported - `--model fibo` and `--model fibo-lite` - along "
                      "with its edit capability. Lite runs at 8 steps with `guidance=1.0` and no "
                      "negative prompt. Weights are gated.",
              'issues': []},
    'mlxvideo': {'status': 'blocked', 'label': 'Blocked',
                 'note': "MLX-Video's image support covers the FLUX line, not this.",
                 'issues': []},
    'diffusionkit': {'status': 'blocked', 'label': 'Predates it',
                     'note': "DiffusionKit implements Stable Diffusion 3 and FLUX.1 only.",
                     'issues': []},
}
