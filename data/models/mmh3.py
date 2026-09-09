"""MiniMax-H3 - model record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'mmh3'
MODALITY = 'video'
NAME = 'MiniMax-H3'
ARCH = '33B joint video+audio diffusion transformer'
LICENSE = 'MiniMax H3 Community License (commercial above $20M needs authorisation)'
CONTEXT = 'text/image-to-video with synchronised audio, up to 15s at 768px short edge'
CONTEXT_LABEL = 'Output'
HF = 'MiniMaxAI/MiniMax-H3'
PARAMS_B = 33

NOTE = (
    "By adoption this is the video model - about 5 million downloads, more than every other model "
    "on this page combined - and the reason to care here is the footprint. The 8-bit MLX build is "
    "a 35 GB download that its packager measures at 21.5 GB resident during generation, which fits "
    "one Mac with room left. LTX-2.5 needs 62 GB peak. It also generates video and audio jointly "
    "rather than producing silent clips and leaving you to score them. The catch is the same one "
    "LTX-2.5 has: no engine on this page loads it. The MLX conversions are driven by "
    "[PipeNetwork/minimax-h3-mlx](https://github.com/PipeNetwork/minimax-h3-mlx), a 73-star "
    "Apache-2.0 port validated against the diffusers reference, with no tagged releases. Note the "
    "licence is a community licence, not open weights - redistribution carries the agreement, "
    "commercial use above $20M of revenue needs separate authorisation, and the grant is "
    "territorially limited."
)

SOURCES = [('Model card', 'https://huggingface.co/MiniMaxAI/MiniMax-H3'),
           ('MLX port', 'https://github.com/PipeNetwork/minimax-h3-mlx'),
           ('MLX 8-bit build with the resident figure',
            'https://huggingface.co/pipenetwork/MiniMax-H3-MLX-8bit')]

SCORES = {'agentic': [], 'coding': []}

# Which engine the card opens on and the glance row names.
BEST_ENGINE = 'mlxvideo'

# Repositories tracker/measure.py harvests for this model.
QUANT_SOURCES = {'mlx': ['pipenetwork/MiniMax-H3-MLX-bf16',
                         'pipenetwork/MiniMax-H3-MLX-8bit',
                         'pipenetwork/MiniMax-H3-MLX-4bit']}

# Measured by tracker/measure.py - do not hand-edit. gb is summed repo bytes;
# bpw is gb*8/PARAMS_B and is omitted for pruned or native-precision builds.
LADDER = {'mlx': [{'label': 'MiniMax-H3-MLX-bf16',
          'repo': 'pipenetwork/MiniMax-H3-MLX-bf16',
          'gb': 66.28,
          'kind': 'native',
          'bpw': None},
         {'label': 'MiniMax-H3-MLX-8bit',
          'repo': 'pipenetwork/MiniMax-H3-MLX-8bit',
          'gb': 35.3,
          'kind': 'native',
          'bpw': None},
         {'label': 'MiniMax-H3-MLX-4bit',
          'repo': 'pipenetwork/MiniMax-H3-MLX-4bit',
          'gb': 25.28,
          'kind': 'native',
          'bpw': None}]}

# Bytes of KV per token at fp16, the context ceiling, and how it was derived.
# None for models with no growing cache (diffusion, TTS).
KV = {'bytes_per_token': None, 'max_context': None, 'derivation': ''}

# Per-engine status. Keys must be engines whose modality matches MODALITY.
ENGINES = {
    'mlxvideo': {'status': 'blocked', 'label': 'Blocked',
                 'note': "MLX-Video implements LTX and Wan. Its README does not mention MiniMax at "
                         "all, and unlike LTX-2.5 nobody has even filed a request for it. The "
                         "project's last push predates this model. Converted MLX weights exist "
                         "regardless, driven by a separate port rather than this engine.",
                 'issues': []},
}
