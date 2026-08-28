"""Ideogram 4 - model record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'ideogram4'
MODALITY = 'image'
NAME = 'Ideogram 4'
ARCH = '9B DiT in an FP8 weight layout'
LICENSE = 'Ideogram licence (gated, manual approval)'
CONTEXT = '1024x1024 typical, 20-step preset'
CONTEXT_LABEL = 'Output'
HF = 'ideogram-ai/ideogram-4-fp8'
PARAMS_B = 9

NOTE = (
    "The one to pick when the image has to contain readable text. Typography is what this model is "
    "built for, and it is the job every general-purpose generator on this page is worst at. The "
    "catch is that it is JSON-caption-native: it expects structured captions, and mflux notes that "
    "plain text prompts are accepted but often underperform, so it is not a drop-in for a prompt you "
    "wrote for FLUX. It also ships sampler presets rather than free step counts, and mflux ignores "
    "`--steps` and `--guidance` on this CLI. Access needs manual approval, not just a click - "
    "request it on the model card and wait, which is the step people miss."
)

SOURCES = [('Model card', 'https://huggingface.co/ideogram-ai/ideogram-4-fp8'),
           ('mflux support', 'https://github.com/filipstrand/mflux/blob/main/src/mflux/models/ideogram4/README.md')]

SCORES = {'agentic': [], 'coding': []}

# Which engine the card opens on and the glance row names.
BEST_ENGINE = 'mflux'

# Repositories tracker/measure.py harvests for this model.
QUANT_SOURCES = {'mlx': ['ideogram-ai/ideogram-4-fp8']}

# Measured by tracker/measure.py - do not hand-edit. gb is summed repo bytes;
# bpw is gb*8/PARAMS_B and is omitted for pruned or native-precision builds.
LADDER = {'mlx': [{'label': 'ideogram-4-fp8',
          'repo': 'ideogram-ai/ideogram-4-fp8',
          'gb': 27.53,
          'kind': 'native',
          'bpw': None}]}

# Bytes of KV per token at fp16, the context ceiling, and how it was derived.
# None for models with no growing cache (diffusion, TTS).
KV = {'bytes_per_token': None, 'max_context': None, 'derivation': ''}

# Per-engine status. Keys must be engines whose modality matches MODALITY.
ENGINES = {
    'mflux': {'status': 'works', 'label': 'Runs',
              'note': "Supported with JSON-caption validation, the published sampler presets, "
                      "quantisation via `mflux-save` and LoRA loading. Two gate steps are needed "
                      "before the first download - request access on the card and wait for "
                      "approval - and doing only the first is the common failure.",
              'issues': []},
    'mlxvideo': {'status': 'blocked', 'label': 'Blocked',
                 'note': "MLX-Video's image support covers the FLUX line, not this.",
                 'issues': []},
    'diffusionkit': {'status': 'blocked', 'label': 'Predates it',
                     'note': "DiffusionKit implements Stable Diffusion 3 and FLUX.1 only.",
                     'issues': []},
}
