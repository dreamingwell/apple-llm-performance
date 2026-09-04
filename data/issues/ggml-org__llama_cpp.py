"""Tracked issues in ggml-org/llama.cpp.

One record, one file. See AGENTS.md for the schema and the rules.
"""

REPO = 'ggml-org/llama.cpp'

# number -> severity / headline / why it matters.
ISSUES = {26694: {'severity': 'high',
         'headline': 'DeepSeek V4 Flash degenerates into repetition and leaks special tokens '
                     'in long agentic sessions on Metal',
         'why': 'The one DeepSeek V4 Flash defect on this engine actually filed against Apple '
                'silicon: a Mac Studio M3 Ultra with 256 GB, Metal with flash attention, serving '
                'the unsloth UD-Q8_K_XL build at 262k context. It degrades over a long agentic '
                'conversation rather than failing outright, which is the hard kind to notice. '
                'Open since 2026-08-07.'},
 
    27742: {'severity': 'medium',
            'headline': 'model: add Qwen3.8-Flash-Next (qwen4exp)',
            'why': 'Merged 2026-08-27, which is what unblocked this architecture. It is on master '
                   'only - no tagged release carries it yet, so a packaged build will not load the '
                   'weights until the next release cuts.'},
    27752: {'severity': 'high',
            'headline': 'model: add GLM-5.3-Flash (glm5next)',
            'why': 'One of three competing open PRs for the same architecture (#27752, #27754, '
                   '#27773). Quants are already published, so the weights are waiting on whichever '
                   'of these lands.'},25522: {'severity': 'medium',
         'headline': 'Gemma 4 crashes with MTP speculative decoding',
         'why': 'MTP is the reason to prefer the GGUF build - the checkpoint ships a draft '
                'head. With MTP off the model runs, so this costs speed rather than '
                'correctness.'},
 25739: {'severity': 'medium',
         'headline': "Google's own Gemma 4 QAT GGUF aborts at vocab load",
         'why': 'Closed 2026-09-03 as not planned, which is a decision not to fix rather than a '
                "fix - the vocab assert on Google's own QAT GGUF still stands. Filed against the "
                'E2B variant, and it matters because the QAT repo is the recommended download, '
                'so this is the default path and not an exotic one. Treat the closed marker as '
                "'no longer being worked on'."},25751: {'severity': 'high',
         'headline': 'Sliding-window attention on Gemma 4 forgets key details',
         'why': "Gemma 4's long context is built on SWA, so this bites exactly where the 256k "
                'window is the reason you picked the model. Quality loss, not a crash, which '
                'makes it harder to notice.'},25967: {'severity': 'high',
         'headline': 'Duplicate GBNF rules with a large tool list break grammar parsing',
         'why': 'Constrained decoding is how tool calls are kept well-formed. Past some number '
                'of tools the generated grammar fails to parse - which is to say the failure '
                'arrives as you add capability to your agent.'},
 26365: {'severity': 'low',
         'headline': 'Kimi K3 full-size vision lives on a branch, not master',
         'why': 'The text backbone is in mainline. This asks for tensor-split support on the '
                'vision branch, which is a useful signal about how finished K3 support is '
                'rather than a blocker for text work.'},
 26382: {'severity': 'medium',
         'headline': 'Same K and V cache type enforced for models with no V cache',
         'why': "GLM-5.2's DSA attention has no V cache to quantise, but the flag pair is "
                'validated as if it did, so you cannot set the K type independently. Costs '
                'memory on the model that has the least to spare.'},
 26894: {'severity': 'medium',
         'headline': 'DFlash drafter fails to bind when the GGUF encodes '
                     'attention.sliding_window',
         'why': 'Blocks speculative decoding on exactly the builds that carry a sliding-window '
                "key. The target model still runs; you lose the draft head's speedup."},27066: {'severity': 'low',
         'headline': 'Adaptive-P sampling is broken on Muse Glimmer',
         'why': 'A sampler, not the model. Pin top-p explicitly and it is a non-issue; listed '
                'because the default sampler config is what most launchers use.'},
 27139: {'severity': 'medium',
         'headline': 'Qwen3.8 tool-calling errors resolved by substituting the Qwen3.6 chat '
                     'template',
         'why': 'The shipped template mis-renders something in the tool path. A workaround '
                'exists and is a single `--chat-template-file`, but until it is fixed the '
                'default template is wrong for agent use.'},
 27141: {'severity': 'high',
         'headline': 'nemotron_h_moe aborts in ggml_ssm_scan during context reservation',
         'why': 'Fires at context reservation, before any token is generated, and the '
                'assertion is in the shared SSM scan rather than a backend - so it is not a '
                'CUDA-only report.'},
 27335: {'severity': 'high',
         'headline': 'Qwen3.8-27B crashes on an M2 Ultra with default settings',
         'why': 'Confirmed on Darwin arm64 with the Metal backend, and on defaults rather than '
                'a tuned command line - the one class of bug that hits you on first run.'},
 27427: {'severity': 'high',
         'headline': 'A ~50 KB request crashes llama-server with exit 139',
         'why': 'Filed on Glimmer. 50 KB is an ordinary agent turn once a file or a diff is in '
                'the prompt, and the process dies rather than rejecting the request.'},
 27428: {'severity': 'low',
         'headline': 'draft-mtp roughly halves prompt processing on a multi-GPU layer split',
         'why': 'Multi-GPU only - a single GPU is fine, so this does not apply to a Mac. '
                'Listed because it is the most active MTP thread and the fix will touch the '
                'shared path.'},
 27720: {'severity': 'medium',
         'headline': 'gpt-oss malformed Harmony channel headers break tool calls',
         'why': 'gpt-oss encodes reasoning and tool calls in Harmony channels; a garbled '
                'header drops the call. Model specific and parser-side, so it is fixable '
                'without touching the weights.'},
 27727: {'severity': 'medium',
         'headline': 'Garbled output from a Qwen3-Coder-Next abliterated GGUF',
         'why': 'Filed against a community abliterated finetune rather than the base weights, '
                'so it may say more about that conversion than about the architecture. Worth '
                'knowing before you blame the model.'},
 27741: {'severity': 'medium',
            'headline': 'Feature request: support Qwen3.8-Flash-Next',
            'why': 'The request thread, still open even though the implementing PR (#27742) merged '
                   'on 2026-08-27. Worth watching for the follow-up fixes rather than as a blocker; '
                   'the remaining gap for this model is MLX, not llama.cpp.'}}
