"""Tracked issues in jundot/omlx.

One record, one file. See AGENTS.md for the schema and the rules.
"""

REPO = 'jundot/omlx'

# number -> severity / headline / why it matters.
ISSUES = {1195: {'severity': 'low',
        'headline': 'MTP speculative decoding not yet supported for Nemotron-H',
        'why': 'A feature request. Nemotron 3.5 Lightning ships MTP weights, so this is speed '
               'left on the table rather than anything broken.'},
 1783: {'severity': 'high',
        'headline': 'Continuous batching prefill collapses at exactly two concurrent requests',
        'why': 'Recovers at higher concurrency, which makes it easy to miss in a benchmark '
               'that jumps straight to eight. Two concurrent requests is the most common real '
               'case.'},
 1794: {'severity': 'medium',
        'headline': 'Hitting the context wall with Gemma 4',
        'why': 'Gemma 4 advertises 256k. This is where users find the practical ceiling on a '
               'Mac, which is set by KV residency rather than by the model.'},
 1862: {'severity': 'medium',
        'headline': 'MiniMax 3 model-type error',
        'why': 'The `minimax_m3_vl` model type is not mapped cleanly. Same root cause as the '
               'loader failure above, seen from the config side.'},
 1927: {'severity': 'medium',
        'headline': 'GLM-5.2-mxfp4 will not load',
        'why': 'Filed against 0.4.4. Matters because mxfp4 is the smallest faithful GLM-5.2 '
               'build, and the alternative affine quants are larger at the same nominal bit '
               'width.'},
 1968: {'severity': 'high',
        'headline': 'MiniMax-M3 fails to load: 2225 parameters not in model (vision_tower)',
        'why': 'The released checkpoint is `minimax_m3_vl` - a vision-language model - and the '
               "text path rejects the vision tower's tensors instead of skipping them."},
 2018: {'severity': 'medium',
        'headline': 'OpenAI endpoint returns 500 while the Anthropic endpoint works',
        'why': 'Both endpoints front the same engine, so a client that speaks Anthropic gets a '
               'working server and a client that speaks OpenAI does not. Worth knowing which '
               'one your agent uses.'},
 2099: {'severity': 'high',
        'headline': 'GLM-5.2 loops',
        'why': 'Repetition loops on the flagship model. A loop burns the context window and '
               'the wall clock without producing a turn, which on a metered agent is worse '
               'than an error.'},
 2137: {'severity': 'medium',
        'headline': 'GLM-5.2-mxfp4 prefill fell from 160-180 tok/s to 40 tok/s on 0.5.0.dev2',
        'why': 'Closed as completed in July 2026, with memory also fluctuating between 400 and '
               '520 GB on a 512 GB M3 Ultra. Kept on the list as the reference point for what '
               'a healthy GLM-5.2 prefill looks like, and as a reminder that a version bump '
               'can cost you a factor of four on this model.'},
 2208: {'severity': 'medium',
        'headline': 'GLM-5.2 cold prefill throttles near the memory ceiling',
        'why': 'GLM-5.2 leaves very little headroom on any Mac that can hold it, so the '
               'adaptive throttle engages in normal use rather than at an extreme.'},
 2216: {'severity': 'high',
        'headline': 'Legitimate gpt-oss tool calls with explicit to=functions.* are dropped',
        'why': 'A regression from a stricter channel check. Calls that are correctly formed '
               'per the Harmony spec get discarded, so the agent sees a turn with no action.'},
 2252: {'severity': 'medium',
        'headline': 'A broken-load DFlash helper poisons concurrent requests to an unrelated '
                    'model',
        'why': 'Cross-contamination between models in the same server, on the Qwen3-Next '
               'batched path specifically.'},
 2307: {'severity': 'high',
        'headline': 'A model-discovery race orphans a loaded engine - 404 GB unreclaimable, '
                    'restart only',
        'why': 'Server-wide, not per model. Discovery racing an in-flight load leaks the whole '
               'resident model; on a 256 GB machine that is the entire budget gone until you '
               'restart.'},
 2469: {'severity': 'high',
        'headline': 'DeepSeek V4 mxfp4 gather_qmm_blocks crashes on float32 activations',
        'why': 'MXFP4 is the quantisation DeepSeek actually released, so this is the preferred '
               'build rather than a fringe one.'},
 2493: {'severity': 'medium',
        'headline': "'Cache signature mismatch' then a severe performance drop on DeepSeek V4",
        'why': 'The prefix cache silently stops being used, so every turn re-prefills. On long '
               'agent conversations that is the difference between seconds and minutes per '
               'turn.'},
 2589: {'severity': 'high',
        'headline': 'Muse Glimmer oQ4e: tool calling broken and decode slow',
        'why': 'Tool calling is the whole point of Glimmer - it leads MCP Atlas. Traced to a '
               'pre-#1839 quantisation, so check which build you pulled before concluding the '
               'model is bad.'},
 2590: {'severity': 'medium',
        'headline': 'Scope clarification: MiniMax M3 long-prefill fixes across Q4 and oQ3',
        'why': 'An open question about which quant tiers the long-prefill fixes cover. Read it '
               'before choosing a MiniMax quant, because the answer decides whether long '
               'prompts work.'},
 2600: {'severity': 'high',
        'headline': 'DFlash speculative decoding renders the cache non-functional on Gemma and '
                    'Glimmer',
        'why': 'Turning on the draft head disables the prefix cache, so you trade a decode '
               'speedup for full re-prefill every turn. On agent workloads that is a net '
               'loss.'},
 2604: {'severity': 'medium',
        'headline': 'Glimmer DFlash can end a turn after reasoning without the forced tool '
                    'call',
        'why': 'The model finishes its reasoning and stops instead of emitting the call. An '
               'agent sees a turn that did nothing, which usually gets retried - so it costs '
               'two turns, not one.'},
 2606: {'severity': 'medium',
        'headline': 'Thinking leaks into content when generation is truncated mid-thought',
        'why': 'A truncated turn returns reasoning as if it were the answer. Downstream that '
               'is indistinguishable from the model answering badly, and it corrupts anything '
               'that parses the reply.'},
 2641: {'severity': 'medium',
        'headline': 'Glimmer is extremely slow with DFlash on',
        'why': 'The companion report to the two above: on this family the draft head currently '
               'costs more than it saves. Run Glimmer without it.'},
 2691: {'severity': 'low',
        'headline': 'Request: an oQ4e-mtp quantisation of Qwen3.8-27B',
        'why': "oMLX's own quant format with the MTP head merged. Until it exists you are "
               'running a generic mlx-community build rather than one tuned for this server.'},
 2747: {'severity': 'high',
        'headline': 'Qwen3.8-27B single-stream decode regressed 36.5 to 24 tok/s on an M3 '
                    'Ultra',
        'why': 'A third of decode throughput, on the model most people will try first, with '
               'the MTP path implicated. This is the number to check against before assuming '
               'an MLX server beats llama.cpp here.'},
 2786: {'severity': 'medium',
        'headline': 'Gemma 4 performance regressed after 0.6.1',
        'why': 'A version-pinning matter rather than an architecture one, but it means the '
               'newest build is not automatically the right one for this model.'},
 2854: {'severity': 'medium',
        'headline': 'No continuous-batching results published for Qwen3.8 and DFlash2',
        'why': 'Continuous batching is the reason to run a server instead of the CLI. '
               'Unmeasured on this architecture means the concurrency story is unproven, not '
               'that it is broken.'},
 2972: {'severity': 'medium',
        'headline': 'Process-global Qwen patches contaminate a resident engine after loading '
                    'another model',
        'why': 'Multi-model serving is a headline oMLX feature; this is the '
               'cross-contamination it can cause. The second model loads and the first one '
               'quietly changes behaviour.'},
 3006: {'severity': 'high',
        'headline': 'GLM-5.2 prefill far below published figures on an M3 Ultra 512 GB',
        'why': 'The published 845 tok/s number depends on the native DSA kernels being '
               'compiled in. This thread is where you find out whether your install actually '
               'has them - the fallback is roughly 30x slower and uses more memory.'},
 3117: {'severity': 'medium',
        'headline': 'Qwen3.8 with the Neural Engine enabled produces zero tokens',
        'why': 'ANE offload is off by default, so this is an opt-in trap rather than a '
               'first-run one - but it is silent, returning an empty completion rather than an '
               'error.'},
 3121: {'severity': 'high',
        'headline': 'DeepSeek V4 Flash decodes at 4-17 tok/s on an M5 Max from residency '
                    'thrash',
        'why': 'Traced to the bundled mlx 0.32.0 keeping a single residency set, so the '
               'weights fault instead of staying wired. A fix is identified in the thread; '
               'until it ships, expect a fraction of the speed ds4 gets on the same machine.'}}
