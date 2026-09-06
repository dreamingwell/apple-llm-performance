"""Hy 4 preview (Tencent) - model record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'hy4'
MODALITY = 'text'
NAME = 'Hy 4 preview'
ARCH = 'hy_v4 - 780B MoE, 78 DSA latent-attention layers, 256 experts, 8 active'
LICENSE = 'Apache-2.0'
CONTEXT = '1,048,576'
HF = 'tencent/Hy4-preview'
PARAMS_B = 780

NOTE = (
    "Notable for its licence more than its scores: Apache-2.0 on 780B is rare, and the models it "
    "sits beside at this size are not - GLM-5.3 moved off MIT to a custom licence, and DeepSeek's "
    "Pro tier has its own terms. Architecturally it is the same shape the frontier has converged "
    "on: 78 layers, every one DSA latent attention with a 512-wide latent plus 64 rope, which "
    "works out to the same 88 KiB per token as GLM-5.2, GLM-5.3 and Hy 4 alike. Tencent publishes "
    "no benchmark table with the weights, so this page carries no scores for it and it does not "
    "appear in the rankings - that is a gap in the evidence, not a judgement. It is a preview "
    "release. Quants are already out ahead of the runtimes, which is the usual pattern here."
)

SOURCES = [('Model card', 'https://huggingface.co/tencent/Hy4-preview'),
           ('config.json', 'https://huggingface.co/tencent/Hy4-preview/raw/main/config.json'),
           ('llama.cpp architecture support',
            'https://github.com/ggml-org/llama.cpp/commits/master/src/llama-arch.cpp')]

SCORES = {'agentic': [], 'coding': []}

# Which engine the card opens on and the glance row names.
BEST_ENGINE = 'llamacpp'

# Repositories tracker/measure.py harvests for this model.
QUANT_SOURCES = {'gguf': ['AngelSlim/Hy4-preview-GGUF'],
                 'mlx': ['inferencerlabs/Hy4-preview-MLX-Q4i',
                         'mlx-community/Hy4-preview-4bit']}

# Measured by tracker/measure.py - do not hand-edit. gb is summed repo bytes;
# bpw is gb*8/PARAMS_B and is omitted for pruned or native-precision builds.
LADDER = {'gguf': [{'label': 'Hy4-preview-Q4_K_M',
           'repo': 'AngelSlim/Hy4-preview-GGUF',
           'gb': 467.29,
           'kind': 'quant',
           'bpw': 4.79},
          {'label': 'Hy4-preview-UD-IQ1_M',
           'repo': 'AngelSlim/Hy4-preview-GGUF',
           'gb': 235.35,
           'kind': 'quant',
           'bpw': 2.41}],
 'mlx': [{'label': 'Hy4-preview-MLX-Q4i',
          'repo': 'inferencerlabs/Hy4-preview-MLX-Q4i',
          'gb': 456.03,
          'kind': 'quant',
          'bpw': 4.68},
         {'label': 'Hy4-preview-4bit',
          'repo': 'mlx-community/Hy4-preview-4bit',
          'gb': 433.36,
          'kind': 'quant',
          'bpw': 4.44}]}

# Bytes of KV per token at fp16, the context ceiling, and how it was derived.
# None for models with no growing cache (diffusion, TTS).
KV = {'bytes_per_token': 89856,
      'max_context': 1048576,
      'derivation': '78 layers, all DSA latent attention, 512 kv_lora_rank + 64 rope - the same '
                    'geometry the GLM-5.x line uses, hence the same per-token cost'}

# Per-engine status. Keys must be engines whose modality matches MODALITY.
ENGINES = {
    'llamacpp': {'status': 'degraded', 'label': 'Master only',
                 'note': "`hy_v4` landed in `src/llama-arch.cpp` on 2026-09-04, one day after "
                         "v0.4.0 cut, so it is on master and not in a release - build from source "
                         "or wait for v0.5.0. AngelSlim's GGUF is the one with real traction at "
                         "121k downloads.",
                 'issues': []},
    'ollama':   {'status': 'blocked', 'label': 'Blocked',
                 'note': "Takes the architecture from llama.cpp, so it is waiting on a release "
                         "carrying `hy_v4` and then an Ollama bump. Not in the library.",
                 'issues': []},
    'lmstudio': {'status': 'blocked', 'label': 'Blocked',
                 'note': "Its llama.cpp engine ships from releases, not master, and its MLX engine "
                         "has no class to call. Blocked on both paths for now.",
                 'issues': []},
    'omlx':     {'status': 'blocked', 'label': 'Blocked',
                 'note': "No `hy_v4` support. Worth watching rather than dismissing: oMLX added "
                         "Tencent's previous generation, `hy_v3`, ahead of mlx-lm, so it has form "
                         "for being the first MLX engine to carry this line.",
                 'issues': []},
    'mlxlm':    {'status': 'blocked', 'label': 'Blocked',
                 'note': "No `hy_v4` in the models directory - no Tencent architecture at all "
                         "today. Both published MLX conversions were made ahead of any runtime "
                         "that can execute them, which is a pattern this page keeps meeting.",
                 'issues': []},
    'vllmmlx':  {'status': 'blocked', 'label': 'Blocked',
                 'note': "Wraps mlx-lm, which has no class for this architecture.",
                 'issues': []},
    'vllmmetal': {'status': 'blocked', 'label': 'Blocked',
                  'note': "Not in `docs/supported_models.md`, and the compute layer is MLX, so it "
                          "inherits the missing model class.",
                  'issues': []},
    'ds4':      {'status': 'none', 'label': 'Out of scope',
                 'note': "ds4 is purpose-built for DeepSeek V4 and the GLM-5.x line. It does not "
                         "carry this architecture.",
                 'issues': []},
}
