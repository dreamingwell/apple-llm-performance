"""Tracked issues in vllm-project/vllm-metal.

One record, one file. See AGENTS.md for the schema and the rules.
"""

REPO = 'vllm-project/vllm-metal'

# number -> severity / headline / why it matters.
ISSUES = {360: {'severity': 'medium',
       'headline': 'RFC: a specialised Metal kernel for MLA paged attention',
       'why': 'Until this exists, latent-attention models fall back to MLX SDPA with no Metal '
              'kernel - which is why the GLM-4.5 row in the support matrix is flagged as slow '
              'and untested.'},
 450: {'severity': 'low',
       'headline': 'RFC: attention backend dispatch',
       'why': 'Design work on how backends get selected per model. Useful for judging how '
              'settled the internals are.'},
 482: {'severity': 'medium',
       'headline': 'Draft-model speculative decoding is net-negative',
       'why': 'Each request re-ingests the full prompt into the draft model, which costs more '
              'than the draft saves. Worth knowing before you reach for spec decode here; the '
              'built-in MTP path (#610) is the one to watch.'},
 610: {'severity': 'medium',
       'headline': 'Built-in MTP draft heads do not yet work with prefix caching on hybrid GDN',
       'why': 'Qwen3.8 is exactly that shape, and it ships an MTP head. Until this lands you '
              'choose between the draft head and the prefix cache rather than having both.'},
 644: {'severity': 'medium',
       'headline': 'Nemotron-H (Mamba-2 + MoE hybrid) paged attention not implemented',
       'why': 'Open request rather than a bug. It is the reason Nemotron 3.5 Lightning does '
              'not load here.'},
 646: {'severity': 'high',
       'headline': 'Mixed batches with top_k enabled on some requests crash the Metal sampler',
       'why': 'Fixed. PR #648 normalises disabled top_k rows to vocab_size and merged '
              '2026-08-27, closing this. It mattered because continuous batching puts requests '
              'with different sampling parameters in one batch, so it was reachable with '
              'ordinary mixed traffic. Kept listed so the fix is dated: you want a build from '
              '2026-08-27 or later.'}}
