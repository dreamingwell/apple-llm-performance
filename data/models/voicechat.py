"""NemotronLabs VoiceChat 11B - model record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'voicechat'
MODALITY = 'audio'
NAME = 'NemotronLabs VoiceChat 11B'
ARCH = '11B end-to-end full-duplex speech-to-speech'
LICENSE = 'NVIDIA Open Model'
CONTEXT = 'speech in, speech out, ~450 ms turn-taking'
CONTEXT_LABEL = 'Behaviour'
HF = 'nvidia/NVIDIA-NemotronLabs-VoiceChat-11B'
PARAMS_B = 11

NOTE = ('Released 3 August 2026 and the most interesting audio model here: it listens and speaks at '
 'the same time rather than taking turns, and it is the first open full-duplex model that can '
 'call tools mid-conversation. Artificial Analysis put it top-three among open speech models '
 'on both conversational dynamics and speech reasoning. mlx-community has published 8-bit and '
 '4-bit builds, so it runs on a laptop.')

SOURCES = [('Model card', 'https://huggingface.co/nvidia/NVIDIA-NemotronLabs-VoiceChat-11B'),
 ('MLX 4-bit build', 'https://huggingface.co/mlx-community/NemotronLabs-VoiceChat-11B-4bit')]

SCORES = {'agentic': [], 'coding': []}

# Which engine the card opens on and the glance row names.
BEST_ENGINE = 'mlxaudio'

# Repositories tracker/measure.py harvests for this model.
QUANT_SOURCES = {'mlx': ['mlx-community/NemotronLabs-VoiceChat-11B-8bit',
         'mlx-community/NemotronLabs-VoiceChat-11B-4bit']}

# Measured by tracker/measure.py - do not hand-edit. gb is summed repo bytes;
# bpw is gb*8/PARAMS_B and is omitted for pruned or native-precision builds.
LADDER = {'gguf': [],
 'mlx': [{'bpw': None,
          'gb': 13.9,
          'kind': 'native',
          'label': 'NemotronLabs-VoiceChat-11B-8bit',
          'repo': 'mlx-community/NemotronLabs-VoiceChat-11B-8bit'},
         {'bpw': None,
          'gb': 9.17,
          'kind': 'native',
          'label': 'NemotronLabs-VoiceChat-11B-4bit',
          'repo': 'mlx-community/NemotronLabs-VoiceChat-11B-4bit'}]}

# Bytes of KV per token at fp16, the context ceiling, and how it was derived.
# None for models with no growing cache (diffusion, TTS).
KV = {'bytes_per_token': None, 'max_context': None, 'derivation': ''}

# Per-engine status. Keys must be engines whose modality matches MODALITY.
ENGINES = {'mlxaudio': {'status': 'works',
              'label': 'Best path',
              'note': 'mlx-community has published 8-bit (13.9 GB) and 4-bit (9.17 GB) builds, '
                      'so a full-duplex voice agent fits on a laptop. What makes this worth '
                      'the footprint over a TTS model is that it is end-to-end '
                      'speech-to-speech - no ASR-then-LLM-then-TTS pipeline, no accumulated '
                      'latency - and it can call tools while the conversation is still going.',
              'issues': []}}
