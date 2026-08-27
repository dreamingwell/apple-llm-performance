"""Magpie TTS Multilingual 357M - model record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'magpie'
MODALITY = 'audio'
NAME = 'Magpie TTS Multilingual 357M'
ARCH = '357M text-to-speech'
LICENSE = 'NVIDIA Open Model'
CONTEXT = '9 languages'
CONTEXT_LABEL = 'Coverage'
HF = 'nvidia/magpie_tts_multilingual_357m'
PARAMS_B = 0.357

NOTE = ("NVIDIA's small multilingual TTS, part of the Nemotron voice-agent stack alongside VoiceChat "
 'and the Nemotron ASR models. At a third of a gigabyte it runs on anything, which makes the '
 'cluster picker beside the point for this one.')

SOURCES = [('Model card', 'https://huggingface.co/nvidia/magpie_tts_multilingual_357m')]

SCORES = {'agentic': [], 'coding': []}

# Which engine the card opens on and the glance row names.
BEST_ENGINE = 'mlxaudio'

# Repositories tracker/measure.py harvests for this model.
QUANT_SOURCES = {'mlx': ['aufklarer/Magpie-TTS-Multilingual-357M-MLX-8bit',
         'aufklarer/Magpie-TTS-Multilingual-357M-MLX-4bit']}

# Measured by tracker/measure.py - do not hand-edit. gb is summed repo bytes;
# bpw is gb*8/PARAMS_B and is omitted for pruned or native-precision builds.
LADDER = {'gguf': [],
 'mlx': [{'bpw': None,
          'gb': 0.43,
          'kind': 'native',
          'label': 'Magpie-TTS-Multilingual-357M-MLX-8bit',
          'repo': 'aufklarer/Magpie-TTS-Multilingual-357M-MLX-8bit'},
         {'bpw': None,
          'gb': 0.26,
          'kind': 'native',
          'label': 'Magpie-TTS-Multilingual-357M-MLX-4bit',
          'repo': 'aufklarer/Magpie-TTS-Multilingual-357M-MLX-4bit'}]}

# Bytes of KV per token at fp16, the context ceiling, and how it was derived.
# None for models with no growing cache (diffusion, TTS).
KV = {'bytes_per_token': None, 'max_context': None, 'derivation': ''}

# Per-engine status. Keys must be engines whose modality matches MODALITY.
ENGINES = {'mlxaudio': {'status': 'works',
              'label': 'Runs',
              'note': 'MLX 8-bit and 4-bit conversions exist from a community packager rather '
                      'than mlx-community, so check the build before trusting it. Pairs '
                      'naturally with the Nemotron ASR models if you are assembling a pipeline '
                      'rather than using an end-to-end model.',
              'issues': []}}
