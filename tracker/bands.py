#!/usr/bin/env python3
"""Fidelity bands and the per-model quant caveats.

Shared tuning constants rather than per-record data, so they live in one small
file instead of the monolith. Changing a band threshold changes how every model
on the page is judged - read AGENTS.md before touching BANDS.
"""

BANDS = [(4.0,
  'full',
  'Full fidelity',
  'At or above 4 bits per weight, which is where measured KL divergence stays low and arithmetic '
  'and tool calling hold up.'),
 (3.0,
  'mild',
  'Reduced fidelity',
  '3 to 4 bits per weight. Reasoning survives this range well, but arithmetic and long '
  'tool-calling chains start to drift. Fine for drafting, worth verifying for agent work.'),
 (2.0,
  'low',
  'Degraded',
  '2 to 3 bits per weight. Measured KL divergence here is roughly 7x the 4-bit tier. Expect '
  'weaker instruction adherence and less reliable tool calls; keep tool schemas small.'),
 (0.0,
  'unusable',
  'Below agentic-usable',
  "Under 2 bits per weight. Unsloth's own guidance is that 1-bit builds should not be used for "
  'agentic use-cases: tool calling breaks down, generations loop without a high presence '
  'penalty, and responses can come back empty. It loads. That is the most that should be claimed '
  'for it.')]

# LM Studio ships two engines, so a model whose MLX build is the better one is
# judged on that ladder instead. Keyed (engine_id, model_id).
FAM_OVERRIDE = {('lmstudio', 'glm47f'): 'mlx', ('lmstudio', 'qwen38'): 'mlx', ('lmstudio', 'gemma4'): 'gguf'}

# What to say when the rung that fits is not full fidelity, or when a nominally
# low tier is better than its name suggests. Keyed (model_id, quant_family).
FIDELITY_NOTES = {('v4flash', 'ds4'): "ds4's 2-bit builds are the exception to the usual warning. Only the routed "
                     'experts are quantised - up and gate at IQ2_XXS, down at Q2_K - while '
                     'shared experts, projections and routing are left untouched, and the result '
                     'is scored against a 100-case fixture of official DeepSeek continuations. '
                     'The project states these behave well under coding agents and call tools '
                     'reliably, which is a stronger claim than anyone makes for a generic 2-bit '
                     'GGUF.',
 ('glm52', 'ds4'): 'Same asymmetric approach as the DeepSeek builds: routed expert gate/up and '
                   'down tensors are quantised while dense and control tensors stay at Q8/F32. '
                   'Two-Mac tensor parallelism needs an IQ2_XXS or Q2_K routed layout '
                   'specifically - a routed Q4 build is rejected for that mode.',
 ('v4pro', 'ds4'): "PRO's routed experts get the same asymmetric treatment. The Q4 pair is a "
                   'layer split for two 512 GB machines rather than a single-machine build.',
 ('gptoss', 'gguf'): 'MXFP4 at 4.23 bits is not a downgrade here - it is the precision OpenAI '
                     'released. There is no higher-fidelity build to reach for, and a Q8 GGUF of '
                     'it would only pad the same weights.',
 ('v4flash', 'gguf'): 'DeepSeek released these experts in MXFP4, so the ladder tops out near 4.5 '
                      'bits rather than 8. The Q8 build is not eight-bit weights; it is the '
                      'native 4-bit experts in a wider container.',
 ('v4pro', 'gguf'): 'Same as Flash: the released experts are already MXFP4, so ~4.4 bits is the '
                    'ceiling, not a compromise.',
 ('gemma4', 'gguf'): 'Google publishes this as a quantisation-aware-trained build, so its 4-bit '
                     'tier lost less than a post-hoc 4-bit of the same model would. Prefer the '
                     'QAT repo over a community requantisation.',
 ('kimik3', 'mlx'): 'These are not quantised down - they are expert-pruned. REAP scores each '
                    'expert and deletes the rest, keeping 179 of 896 per layer in the 350 GB '
                    "build, so the surviving weights are near lossless mxfp4 while the model's "
                    'capacity is cut by four fifths. A bits-per-weight figure would flatter it. '
                    'The publisher documents the damage candidly, including Chinese output '
                    'looping in the REAP-80 build, and code holding up better than language '
                    'because code experts cluster densely.',
 ('kimik3', 'gguf'): 'Every Kimi K3 GGUF tier that fits any Mac cluster is under 2.5 bits per '
                     'weight, and the ones that fit two 256 GB machines are 1.3 to 1.7 bits - '
                     'squarely inside the band its own quantiser warns against for agentic use. '
                     'The 88.3 Terminal-Bench figure was not measured on anything you can run '
                     'here.',
 ('q38fnext', 'gguf'): 'The only published GGUF is a single UD-IQ1_S at 72.5 GB, which works out '
                       'to 3.22 bits per weight against the full 180B checkpoint because the 51B '
                       'n-gram embedding table dominates it. There is no ladder to choose from, '
                       'and no mainline loader for the file either.',
 ('qwenmax', 'gguf'): 'Nothing on this ladder is comfortable. The smallest unpruned build is '
                      '1.30 bits per weight, and the first tier that clears 2 bits is 656.6 GB. '
                      'The REAP-256GB and REAP-512GB builds are expert-pruned to hit those '
                      'memory targets, which trades capacity for fit rather than precision.',
 ('qwenmax', 'mlx'): 'Only one published MLX build is not expert-pruned, and it is 805.6 GB. '
                     'Everything that fits a realistic Mac cluster has had between half and '
                     'three quarters of its experts deleted.',
 ('qcnext', 'mlx'): 'The MLX ladder stops at 4-bit (44.8 GB) - there is no 3-bit rung - while '
                    'the GGUF ladder runs all the way down to 18.9 GB. On a 32 or 48 GB machine '
                    'that difference decides whether the model fits at all.',
 ('glm47', 'mlx'): 'The MLX ladder has no 3-bit rung, so it steps straight from 4-bit at 198.6 '
                   'GB down to expert-pruned REAP builds. The GGUF ladder is finer-grained in '
                   'exactly the range that matters on a 256 GB machine.'}
