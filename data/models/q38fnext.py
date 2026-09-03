"""Qwen3.8-Flash-Next - model record.

One record, one file. See AGENTS.md for the schema and the rules.
"""

ID = 'q38fnext'
MODALITY = 'text'
NAME = 'Qwen3.8-Flash-Next'
ARCH = 'MoE 125B + 51B n-gram embedding / 6B active · Gated DeltaNet + Qwen Sparse Attention'
LICENSE = 'Qwen Community 1.0'
CONTEXT = '262k (1M on the hosted version)'
HF = 'Qwen/Qwen3.8-Flash-Next'
PARAMS_B = 180
# Parameters read per decoded token, the divisor in the decode ceiling:
# published as 6B active; the 51B n-gram table is looked up, not streamed.
ACTIVE_PARAMS_B = 6

NOTE = ('Qwen calls this an experimental preview of the architecture behind Qwen4, and the numbers '
 'are the strongest per active parameter on this page: 6B active beats Qwen3.8-27B on every '
 'shared benchmark, and its SWE-bench Multilingual of 81.0 leads the page outright. Three '
 'genuinely new pieces - Qwen Sparse Attention at micro-block granularity, gated residuals, '
 'and a 51B n-gram embedding table designed to be offloaded. That last one is why the '
 'checkpoint is 180B on disk against a stated 125B. llama.cpp merged the `qwen4exp` '
 'architecture on 2026-08-27, so this is runnable on Apple silicon for the first time - '
 'from a master build, not a release, and the GGUF ladder filled out from a single 1-bit '
 'tier to Q4_K_XL within days. oMLX went further and vendored its own qwen4_exp '
 'support in v0.6.3, so the fastest published numbers on Apple silicon are now on '
 'MLX rather than GGUF - with the concurrency caveats on that tab.')

SOURCES = [('Model card with full tables', 'https://huggingface.co/Qwen/Qwen3.8-Flash-Next'),
 ('Qwen blog', 'https://qwen.ai/blog?id=qwen3.8-flash-next')]

SCORES = {'agentic': [('Toolathlon Verified', '73.5'),
             ('CoWorkBench', '73.9'),
             ('JobBench', '55.7'),
             ('Agents’ Last Exam', '24.3')],
 'coding': [('SWE-bench Multilingual', '81.0'),
            ('SWE-bench Pro', '62.5'),
            ('LiveCodeBench v6', '91.9'),
            ('DeepSWE 1.1', '58.7')]}

# Which engine the card opens on and the glance row names.
BEST_ENGINE = 'omlx'

# Repositories tracker/measure.py harvests for this model.
QUANT_SOURCES = {'gguf': ['unsloth/Qwen3.8-Flash-Next-GGUF'],
                 'mlx': ['Jundot/Qwen3.8-Flash-Next-oQ4e-mtp',
                         'Vontra/Qwen3.8-Flash-Next-MLX-4bit',
                         'Vontra/Qwen3.8-Flash-Next-MLX-oQ4-MTP',
                         'Sawfwair/Qwen3.8-Flash-Next-MLX-Mixed-2bit']}

# Measured by tracker/measure.py - do not hand-edit. gb is summed repo bytes;
# bpw is gb*8/PARAMS_B and is omitted for pruned or native-precision builds.
LADDER = {'gguf': [{'label': 'Qwen3.8-Flash-Next-BF16',
           'repo': 'unsloth/Qwen3.8-Flash-Next-GGUF',
           'gb': 354.03,
           'kind': 'quant',
           'bpw': 15.73},
          {'label': 'Qwen3.8-Flash-Next-Q8_0',
           'repo': 'unsloth/Qwen3.8-Flash-Next-GGUF',
           'gb': 188.23,
           'kind': 'quant',
           'bpw': 8.37},
          {'label': 'Qwen3.8-Flash-Next-UD-Q6_K_XL',
           'repo': 'unsloth/Qwen3.8-Flash-Next-GGUF',
           'gb': 169.17,
           'kind': 'quant',
           'bpw': 7.52},
          {'label': 'Qwen3.8-Flash-Next-UD-Q5_K_XL',
           'repo': 'unsloth/Qwen3.8-Flash-Next-GGUF',
           'gb': 158.29,
           'kind': 'quant',
           'bpw': 7.03},
          {'label': 'Qwen3.8-Flash-Next-UD-Q4_K_XL',
           'repo': 'unsloth/Qwen3.8-Flash-Next-GGUF',
           'gb': 111.33,
           'kind': 'quant',
           'bpw': 4.95},
          {'label': 'Qwen3.8-Flash-Next-UD-Q3_K_XL',
           'repo': 'unsloth/Qwen3.8-Flash-Next-GGUF',
           'gb': 89.99,
           'kind': 'quant',
           'bpw': 4.0},
          {'label': 'Qwen3.8-Flash-Next-UD-IQ3_XXS',
           'repo': 'unsloth/Qwen3.8-Flash-Next-GGUF',
           'gb': 81.96,
           'kind': 'quant',
           'bpw': 3.64},
          {'label': 'Qwen3.8-Flash-Next-UD-Q2_K_XL',
           'repo': 'unsloth/Qwen3.8-Flash-Next-GGUF',
           'gb': 78.87,
           'kind': 'quant',
           'bpw': 3.51},
          {'label': 'Qwen3.8-Flash-Next-UD-IQ1_M',
           'repo': 'unsloth/Qwen3.8-Flash-Next-GGUF',
           'gb': 74.54,
           'kind': 'quant',
           'bpw': 3.31}],
 'mlx': [{'label': 'Qwen3.8-Flash-Next-MLX-oQ4-MTP',
          'repo': 'Vontra/Qwen3.8-Flash-Next-MLX-oQ4-MTP',
          'gb': 113.33,
          'kind': 'quant',
          'bpw': 5.04},
         {'label': 'Qwen3.8-Flash-Next-oQ4e-mtp',
          'repo': 'Jundot/Qwen3.8-Flash-Next-oQ4e-mtp',
          'gb': 106.29,
          'kind': 'quant',
          'bpw': 4.72},
         {'label': 'Qwen3.8-Flash-Next-MLX-Mixed-2bit',
          'repo': 'Sawfwair/Qwen3.8-Flash-Next-MLX-Mixed-2bit',
          'gb': 73.1,
          'kind': 'quant',
          'bpw': 3.25}]}

# Bytes of KV per token at fp16, the context ceiling, and how it was derived.
# None for models with no growing cache (diffusion, TTS).
KV = {'bytes_per_token': 24576,
 'max_context': 262144,
 'derivation': '12 of 48 layers use Qwen Sparse Attention at micro-block granularity with a '
               '2048 budget, so this is an upper bound; the other 36 are Gated DeltaNet'}

# Per-engine status. Keys must be engines whose modality matches MODALITY.
ENGINES = {'llamacpp': {'status': 'degraded',
              'label': 'Master only',
              'note': "Support landed on 2026-08-27: `qwen4exp` is now in "
                      "`src/llama-arch.cpp`. It is on master only - no tagged release carries it "
                      "yet, so a packaged build or a distro binary will still refuse the weights. "
                      "Build from source until the next release cuts. Three further PRs are open "
                      "against the same architecture for fixes, so treat the implementation as "
                      "new rather than settled.",
              'issues': ['ggml-org/llama.cpp#27742', 'ggml-org/llama.cpp#27741']},
 'ollama': {'status': 'blocked',
            'label': 'Blocked',
            'note': "Not in the library. llama.cpp gained the architecture on 2026-08-27, so this is now waiting on an Ollama bump to a build that carries it rather than on the architecture itself.",
              'issues': []},
 'lmstudio': {'status': 'blocked',
              'label': 'Blocked',
              'note': "Nothing curated in either format. Its llama.cpp engine will pick this up once LM Studio ships a build from master; its MLX engine stays blocked until mlx-lm merges a qwen4_exp class.",
              'issues': []},
 'omlx': {'status': 'degraded',
          'label': 'Fastest, with caveats',
          'note': 'oMLX added first-class `qwen4_exp` support in v0.6.3 on 2026-08-27 and '
                   'improved it again in v0.6.4 two days later, with its own vendored '
                   'implementation rather than waiting for mlx-lm - the same move it made for '
                   'DeepSeek V4. The maintainer publishes measured numbers on an M3 Ultra 512 GB '
                   'with the first-party `Jundot/Qwen3.8-Flash-Next-oQ4e-mtp` build: 1,061 tok/s '
                   'prefill and 53.6 tok/s generation at 4k, still 1,114 and 45.9 at 32k, with '
                   'Lightning MTP worth 2.3x to 2.6x on generation. That makes this the fastest '
                   'published path to this model on Apple silicon by a wide margin. Read the '
                   'defects before serving it, though: two concurrent requests fail outright on '
                   'the sparse-attention indexer, and QSA prefix-cache reuse is broken across '
                   'turns, so a single-user session is the configuration that actually works '
                   'today. Text and image input; video is unsupported.',
              'issues': ['jundot/omlx#3293', 'jundot/omlx#3294', 'jundot/omlx#3300', 'jundot/omlx#3303']},
 'vllmmlx': {'status': 'blocked',
             'label': 'Blocked',
             'note': "Wraps mlx-lm, which has no qwen4 class. Nothing to wrap until that PR merges.",
              'issues': ['ml-explore/mlx-lm#1788']},
 'mlxlm': {'status': 'blocked',
           'label': 'Blocked',
           'note': "The models directory carries `qwen3_next` but nothing for qwen4. A PR adding `qwen4_exp` is open and unmerged, and it is the gate for every MLX engine on this page - llama.cpp has already moved, MLX has not.",
              'issues': ['ml-explore/mlx-lm#1788']},
 'vllmmetal': {'status': 'blocked',
               'label': 'Blocked',
               'note': "The matrix covers Qwen3.5 through 3.8, not the qwen4_exp preview architecture, and the compute layer is MLX so it inherits the same missing model class.",
              'issues': ['ml-explore/mlx-lm#1788']},
 'ds4': {'status': 'none',
         'label': 'Out of scope',
         'note': 'Not one of the three checkpoints ds4 loads.',
         'issues': []}}
