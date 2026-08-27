"""Tracked issues in ollama/ollama.

One record, one file. See AGENTS.md for the schema and the rules.
"""

REPO = 'ollama/ollama'

# number -> severity / headline / why it matters.
ISSUES = {14116: {'severity': 'medium',
         'headline': 'Tiered context length can exhaust VRAM',
         'why': 'The automatic context sizing can commit more memory than the machine has. On '
                'a Mac that is unified memory, so it is the whole machine rather than just the '
                'model.'},
 15813: {'severity': 'critical',
         'headline': 'Metal backend crash on Apple M5: bfloat/half type mismatch',
         'why': 'An M5-specific crash in the Metal matmul path. If you are buying an M5 '
                'machine, this is the one to check is closed before you plan around Ollama on '
                'it.'},
 17323: {'severity': 'high',
         'headline': 'Bare-JSON tool-call models silently drop content generated after the '
                     'call',
         'why': 'The call survives and the accompanying text does not. Silent truncation is '
                'worse than an error because the agent proceeds on a partial turn.'},
 17569: {'severity': 'medium',
         'headline': 'x/mlxrunner panics importing a plain Qwen3 MLX 4-bit model',
         'why': "An index-out-of-range in the MLX runner's dense MLP forward. Importing an "
                'ordinary mlx-community checkpoint is a normal thing to want to do.'},
 17638: {'severity': 'high',
         'headline': "gpt-oss: HTTP 500 'error parsing tool call' on a call its own model "
                     'generated',
         'why': "The server rejects output produced by the model it shipped. From the agent's "
                'side it is a hard failure on a turn that was otherwise correct.'},
 17656: {'severity': 'high',
         'headline': 'muse-glimmer:30b-mlx is built from nvfp4-dflash layers, not real MLX '
                     'weights',
         'why': 'The tag says MLX and the manifest says something else, so you may not be '
                'running what you think you are. Worth knowing generally: an Ollama tag is a '
                'manifest, not a guarantee about the underlying build.'},
 17776: {'severity': 'high',
         'headline': 'Qwen3.8-27B MTP variants are 2x slower than non-MTP on Apple Silicon',
         'why': 'Speculative decoding making decode twice as slow is the opposite of the '
                'intent. On this model MTP is the main reason to prefer one engine over '
                'another, so a negative result here matters.'},
 17783: {'severity': 'medium',
         'headline': 'gemma4:31b-mlx grows in memory over a session',
         'why': 'Resident size climbing during use, on the MLX path. Matters most on a machine '
                'sized close to the model.'},
 17878: {'severity': 'medium',
         'headline': 'Embeddings silently return all-zero vectors under sustained load',
         'why': 'HTTP 200, plausible usage numbers, and useless vectors. Not an LLM path, but '
                'it says something about how failures surface here.'}}
