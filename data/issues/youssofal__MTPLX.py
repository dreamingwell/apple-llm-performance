"""Tracked issues in youssofal/MTPLX.

One record, one file. See AGENTS.md for the schema and the rules.
"""

REPO = 'youssofal/MTPLX'

# number -> severity / headline / why it matters.
ISSUES = {65: {'severity': 'medium',
      'headline': 'GLM-4.7 PRISM passes inspect after a hand-repaired config, then MTP '
                  'generation crashes on fa_idx',
      'why': 'Closed as completed on 2026-05-25. Kept because of how the reporter got that '
             'far: the MLX conversion had zeroed `num_nextn_predict_layers` and dropped the '
             'draft tensors, and he had to restore both by hand on a 512 GB M3 Ultra before '
             'the engine would look at it. That is the shape of every blocked GLM cell here.'},
 107: {'severity': 'low',
       'headline': '"No config.json" when checking Youssofal/Gemma4-MTPLX-Optimized-Quality',
       'why': 'The Gemma 4 artifact is a pair bundle - `mtplx_pair.json` plus `target/` and '
              '`assistant/` - so its root has no config.json by design. Closed, but it dates '
              'when the preflight learned to recognise a bundle root instead of reporting a '
              'broken download.'},
 123: {'severity': 'low',
       'headline': 'Ornith pulled from Hugging Face reports "missing needed mtplx files"',
       'why': 'Closed as completed on 2026-07-31. The same complaint as #359 one release '
              'earlier, and the reason a Qwen-family checkpoint that the engine will happily '
              'serve autoregressive can still be unreachable from the app.'},
 265: {'severity': 'high',
       'headline': 'batch=2 is 0.41x single-request throughput on Qwen3.8-27B, M3 Max 128 GB',
       'why': 'Two concurrent requests are slower than running them one after the other. The '
              'default scheduler is `serial` for exactly this reason, which makes MTPLX a '
              'single-user engine in practice however many clients point at it.'},
 286: {'severity': 'low',
       'headline': 'Open request for an MTPLX vs oMLX context ladder on Qwen3.8-27B, M3 Max '
                   '128 GB',
       'why': 'The comparison a reader wants and nobody has published. Every speed figure for '
              'this engine is currently the project measuring itself.'},
 293: {'severity': 'medium',
       'headline': 'A verify cycle costs 1.6-2.0x an AR forward where the bench implies '
                   '1.2-1.3x',
       'why': 'Filed by the project against its own numbers. It sets the ceiling on the '
              'speedup: at depth 5 the verify pass already costs as much as it saves, which is '
              'why the Qwen family is capped at depth 3.'},
 299: {'severity': 'medium',
       'headline': "Forge fails to build an MTP artifact from Qwen's own official checkpoints "
                   'on an M1',
       'why': 'Forge is the documented route out of every "loads but no draft head" cell on '
              'this engine. If it will not run on the upstream weights, that route is closed '
              'and the only working artifacts are the ones the project publishes itself.'},
 308: {'severity': 'low',
       'headline': 'Qwen3.8 DFlash2 cannot be selected as a first-class backend',
       'why': 'A feature request. `z-lab/Qwen3.8-27B-DFlash2` is a separate five-layer draft '
              'architecture; MTPLX can benchmark it but `serve` cannot use it, so the only '
              'draft path in production is the native head.'},
 323: {'severity': 'high',
       'headline': 'Coding-agent sessions never reach the SSD session cache, so 100K+ contexts '
                   're-prefill on every restart',
       'why': 'A `live_ref_only` gate keeps agent sessions out of the cold tier. The SSD '
              'session cache is on by default and advertised as restoring sessions '
              'near-instantly; for the agent workload this engine is aimed at, it does not '
              'engage.'},
 341: {'severity': 'high',
       'headline': "Nemotron-H detection ignores `mtp_layers_block_type`, so NVIDIA's own "
                   'config crashes on AttributeError',
       'why': 'The one place with measured Apple-silicon numbers for this family. The reporter '
              'added `"mtp_hybrid_override_pattern": "*E"` by hand and got 88.28% acceptance '
              'and 46.27 -> 50.00 tok/s, a 1.081x gain. He also notes Forge offers depths 1-3 '
              'while the backend rejects anything above 1.'},
 343: {'severity': 'high',
       'headline': 'Streaming turns die with "request cancelled via POST /v1/mtplx/cancel" '
                   'when nothing cancelled them',
       'why': 'An early tool-call cancel races a 250 ms queue poll. The client sees a '
              'deliberate cancellation, so an agent treats a lost turn as a user abort and '
              'stops rather than retrying.'},
 348: {'severity': 'critical',
       'headline': 'Uncapped decode-lease reservation with no OOM handling crashes Metal on '
                   'long sessions',
       'why': 'The failure mode is a hard crash of the whole daemon, not a rejected request, '
              'so every other session on the server dies with it. Long sessions are the '
              'workload this engine is sold for.'},
 358: {'severity': 'low',
       'headline': 'No periodic SSE comment-line heartbeats',
       'why': 'A feature request. Without keep-alives a long prefill looks like a dead '
              'connection to any proxy or client with a read timeout, which is the common way '
              'a large-context turn appears to fail.'},
 359: {'severity': 'high',
       'headline': 'The app refuses custom Hugging Face models that `mtplx inspect` reports as '
                   'runnable',
       'why': 'The app requires `mtplx_runtime.json`, which only `mtplx forge` ever writes, so '
              'no third-party repo has one. The engine classifies the same folder as '
              'family-compatible-unverified with `can_run: true`. Every degraded cell on this '
              'engine is CLI-only for this reason, and the app blames an incomplete download.'},
 360: {'severity': 'high',
       'headline': 'macOS kills the Python backend under memory pressure during long Qwen CLI '
                   'agent sessions',
       'why': 'Distinct from #348: here the OS reclaims the process rather than Metal failing '
              'an allocation. Same consequence for the user, and it is why headroom above the '
              "artifact's stated peak matters on this engine."},
 376: {'severity': 'high',
       'headline': "The compact tool contract truncates 'Declared tools' at 1200 characters, "
                   'dropping trailing tools',
       'why': 'Still reported present in 2.9.2 after the endpoints went passthrough by '
              'default. A tool the model never sees is a capability the agent silently loses, '
              'which reads as the model being bad at tool use.'},
 383: {'severity': 'high',
       'headline': 'Cross-session preemption produces a 45 minute time-to-first-token at 175K '
                   'context',
       'why': 'Not a slowdown, a stall. It is the concrete cost of running this engine as a '
              'shared server, and it compounds with #323 because the preempted session cannot '
              'be restored from the cold tier either.'},
 390: {'severity': 'high',
       'headline': 'The qwen4_exp lane requires ngram-manifest.json and mtplx_runtime.json '
                   'that no published artifact ships',
       'why': "Filed 2026-08-29. `qwen4_runtime.py` loads the manifest unconditionally, "
              '`forge build` has no code that emits one, and neither the third-party artifact '
              "the reporter used nor Youssofal's own Flash-Next uploads contain it. It is the "
              'gate on the only MLX path to Qwen3.8-Flash-Next.'}}
