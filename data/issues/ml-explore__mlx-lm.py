"""Tracked issues in ml-explore/mlx-lm.

One record, one file. See AGENTS.md for the schema and the rules.
"""

REPO = 'ml-explore/mlx-lm'

# number -> severity / headline / why it matters.
ISSUES = {1162: {'severity': 'high',
        'headline': 'Qwen3-Next hybrid cache silently fails, breaking the prompt cache',
        'why': 'Silent, and it removes prefix reuse - the single biggest win on multi-turn '
               'agent traffic. Every MLX server that wraps mlx-lm inherits it, so the model '
               'looks fine while every turn re-prefills.'},
 1192: {'severity': 'high',
        'headline': 'The DeepSeek V4 port thread',
        'why': 'Where the community port was developed and tested before PR #1233. Useful for '
               'finding out what already works in a fork if you do not want to wait for the '
               'merge.'},
 1233: {'severity': 'critical',
        'headline': 'PR: DeepSeek V4 model class, still open',
        'why': 'This is the entire MLX blocker for DeepSeek V4. Until it merges there is no '
               '`deepseek_v4` in mlx-lm, so no MLX server that wraps mlx-lm can load the '
               'architecture no matter which quant you download.'},
 1242: {'severity': 'medium',
        'headline': 'Error loading mlx-community/gemma-4-e4b-it-4bit',
        'why': 'The published small-variant quant does not load cleanly.'},
 1281: {'severity': 'medium',
        'headline': 'Request: add DeepSeek V4 to mlx_lm',
        'why': 'The demand-side thread for the PR above. Useful as a temperature check on '
               'whether the port is moving.'},
 1332: {'severity': 'high',
        'headline': 'DeepSeek-V4 unbounded Metal residency during decode',
        'why': 'Dies at ~11k decode tokens with metal::malloc resource-limit exceeded. Even '
               'once the architecture lands, this has to be fixed before the model is '
               'servable.'},
 1335: {'severity': 'high',
        'headline': 'Tool calls dropped when the tokenizer merges the tool-call start marker',
        'why': 'The json_tools parser never matches, so the call is returned as plain text. '
               'Architecture-independent and specific to agent use.'},
 1352: {'severity': 'high',
        'headline': 'Gemma 4 with thinking enabled returns only reasoning, content empty',
        'why': 'The visible reply comes back blank whenever thinking is on.'},
 1401: {'severity': 'critical',
        'headline': 'PR: Add MiniMax-M3 (text backbone) - unmerged',
        'why': 'The only route to M3 on MLX, open since 2026-08-24. The only route to M3 on '
               'MLX.'},
 1404: {'severity': 'medium',
        'headline': 'DeepSeek V4 Flash drifts from Simplified to Traditional Chinese',
        'why': 'Filed against the mlx-vlm DeepSeek path, which is the only working MLX route '
               'today. A quality defect rather than a load failure, and confined to CJK '
               'output.'},
 1418: {'severity': 'critical',
        'headline': 'GLM-5.2 fails to load — missing per-layer indexer params',
        'why': "The loader expects a DeepSeek-V3.2-style indexer on every layer, but GLM-5.2's "
               'IndexShare places them on a subset. mlx-community/GLM-5.2-mxfp4 aborts with '
               '285 missing parameters.'},
 1443: {'severity': 'high',
        'headline': 'DSA Indexer sparse top-k evicts attention sinks',
        'why': 'Past index_topk (2048) the indexer drops the attention sinks and decode '
               'collapses into repetition — a sharp cliff, not drift. Hits every '
               'sparse-attention model: DeepSeek V3.2/V4 and GLM-5.2 both decode through this '
               'module.'},
 1446: {'severity': 'medium',
        'headline': 'ArraysCache is not trimmable',
        'why': 'The structural reason the k=1 cap exists — GDN state layers cannot be rolled '
               'back on draft rejection. Same root cause as #730.'},
 1493: {'severity': 'critical',
        'headline': 'Generation hangs at 0% CPU right after prompt processing',
        'why': 'A wedge, not a slowdown - the server stops doing work with no error.'},
 1572: {'severity': 'high',
        'headline': '>300GB models trip the GPU watchdog at load',
        'why': 'load_model() ends with one mx.eval(model.parameters()), building a single '
               'enormous Metal command buffer. At ~390GB it hits '
               'kIOGPUCommandBufferCallbackErrorTimeout and the error escapes uncaught, '
               'hard-aborting the process. GLM-5.2 at 4-bit is 372-475GB.'},
 1573: {'severity': 'medium',
        'headline': 'RotatingKVCache.to_quantized() blocks --kv-bits on sliding-window layers',
        'why': "Gemma 4's sliding-window attention cannot use a quantised KV cache."},
 1662: {'severity': 'high',
        'headline': "Models that discard update_and_fetch's return leak one Metal buffer per "
                    'layer per generation',
        'why': 'The general form of the DeepSeek V4 residency growth. Any model class written '
               'with that mistake leaks for as long as the process lives, so it shows up as a '
               'long-run failure, not a first-run one.'}}
