"""Tracked issues in antirez/ds4.

One record, one file. See AGENTS.md for the schema and the rules.
"""

REPO = 'antirez/ds4'

# number -> severity / headline / why it matters.
ISSUES = {805: {'severity': 'medium',
       'headline': 'Disk KV cache can be reused across different weights sharing a model_id',
       'why': 'Swap quantisations and the cache from the old weights can be restored against '
              'the new ones. Silent wrong-context, and it survives a restart because that is '
              'what the disk cache is for.'},
 807: {'severity': 'medium',
       'headline': 'DeepSeek V4 PRO 0813 support',
       'why': 'The 0813 refresh is not yet a supported checkpoint. ds4 is deliberately narrow, '
              'so a newer PRO release is a tracked task rather than something that just '
              'loads.'},
 816: {'severity': 'high',
       'headline': 'Stateless chat clients never extend the live KV session on Flash/Metal',
       'why': 'Most agent clients are stateless - they resend a longer prompt each turn. If '
              'the session is not extended, the disk KV cache and prefix reuse stop paying, '
              'which is the main reason to run ds4.'},
 836: {'severity': 'medium',
       'headline': 'Possible ds4-server memory leak',
       'why': 'Unconfirmed. On a machine where the model already occupies most of RAM, a slow '
              'server-side leak ends as an OOM rather than as swap.'},
 839: {'severity': 'low',
       'headline': 'No tagged releases, which blocks downstream packaging',
       'why': 'You build from a moving main branch. The project describes itself as beta and '
              'fast-changing, so pin a commit yourself if you care about reproducibility.'},
 845: {'severity': 'high',
       'headline': '--layers maps a shard as N disjoint Metal buffers, about 77x slower decode',
       'why': 'Hits the distributed path specifically. If you are splitting DeepSeek V4 PRO or '
              'GLM-5.2 across two Macs, this is the first thing to check when the numbers look '
              'impossible.'},
 851: {'severity': 'low',
       'headline': 'DeepSeek V4 Flash vision is not supported',
       'why': 'Text only today. Irrelevant for coding and terminal work; relevant if you '
              'wanted the same engine for screenshots.'},
 853: {'severity': 'high',
       'headline': 'BPE merge loop is O(n squared): large prompts take minutes to tokenize',
       'why': 'Tokenization is pure fixed cost before any GPU work. An agent that pastes a '
              'file into the prompt pays it on every turn, and it does not show up in the '
              'tok/s figures.'},
 860: {'severity': 'medium',
       'headline': 'ds4 crashes the machine on launch for one reporter',
       'why': 'A single report without a resolved cause. Listed because a full-machine crash '
              'is a different risk class from a process crash.'}}
