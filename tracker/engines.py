"""Engine roster and the per-model x per-engine compatibility matrix.

The tracker began as a vllm-mlx page, which made it read as though MLX were the
only way to run a model on a Mac. It is not, and for several architectures it is
the worst way. This module carries every runtime worth naming, what surface it
presents (app, CLI, server), whether it speaks an HTTP API you can point an
agent at, and per model: does it run, what does it weigh in that engine's own
quantisation, and what is broken.

Status vocabulary, used for both the tab pill and the fit maths:
  works    - loads and serves today, no architecture-level blocker
  degraded - loads, but with a defect that matters for agentic use
  blocked  - the architecture or the weights are not there
  none     - out of scope by design (a single-model engine, mostly)
"""

ENGINES = [
    {"id": "llamacpp", "name": "llama.cpp", "fmt": "GGUF",
     "surface": "CLI + llama-server", "api": "OpenAI-compatible",
     "api_kind": "api", "repo": "ggml-org/llama.cpp", "lic": "MIT",
     "api_detail": {
         "endpoints": "OpenAI: /v1/models, /v1/chat/completions, /v1/completions, /v1/responses, /v1/embeddings, plus token-counting routes for chat and responses. Anthropic: /v1/messages and /v1/messages/count_tokens. Also /slots prompt-cache save/restore, Prometheus /metrics, and real-time completion control.",
         "streaming": "SSE on every chat surface. Returns a standard `usage` object plus a `timings` block that reports `cache_n` - how many prompt tokens were reused from cache - which is the number you want when tuning an agent loop.",
         "tools": "Native tool-call styles per model family with a generic fallback, `tool_choice`, and `parallel_tool_calls` gated on what the jinja template supports. Arguments stream as deltas.",
         "structured": "`response_format` accepts both `json_object` and `json_schema`, enforced by GBNF grammar sampling at the token level rather than validated afterwards.",
         "concurrency": "Parallel slots (`-np`), with per-slot prompt caches you can persist to disk.",
         "gotcha": "Tool use requires the `--jinja` flag on both the OpenAI and Anthropic surfaces - without it `tools` is silently inert. The project's own docs decline to claim spec compliance: “no strong claims of compatibility with OpenAI API spec is being made”.",
     },
     "what": "The reference GGUF runtime, with a first-class Metal backend. New architectures land "
             "here earlier and more completely than anywhere else on this page, and Ollama, LM Studio, "
             "Jan, KoboldCpp and most other local runners are downstream of it. `llama-server` exposes "
             "an OpenAI-compatible endpoint, so nothing here is GUI-only."},
    {"id": "ollama", "name": "Ollama", "fmt": "MLX on Apple Silicon, GGUF elsewhere",
     "surface": "Background server + CLI", "api": "OpenAI-compatible, plus its own /api",
     "api_kind": "api", "repo": "ollama/ollama", "lic": "MIT",
     "api_detail": {
         "endpoints": "OpenAI: /v1/models, /v1/models/{model}, /v1/chat/completions, /v1/completions, /v1/embeddings, /v1/responses. Anthropic-compatible surface as well. Its own richer /api/* routes sit alongside.",
         "streaming": "Yes, with `stream_options`. The only engine here that publishes an explicit checkbox matrix of what it does and does not implement, which is worth more than most of the feature lists.",
         "tools": "Tools yes, but **`tool_choice` is not implemented** - you cannot force a specific call or require that one happen. Also missing: `logprobs`, `n`, `logit_bias`, `user`.",
         "structured": "`response_format` and JSON mode supported.",
         "concurrency": "Serves concurrently with automatic model loading and unloading.",
         "gotcha": "`/v1/responses` is non-stateful only: no `previous_response_id`, no `conversation`. And because MLX is now the default engine on Apple Silicon, a tag can resolve to a different backend than you expect.",
     },
     "what": "One-command pulls from a curated library, running as a launch-agent server. Since v0.30 "
             "(May 2026) MLX is the default engine on Apple Silicon rather than llama.cpp, which is the "
             "single most important thing to know about it here: on a Mac, Ollama inherits MLX's "
             "architecture coverage for the models it serves through that path."},
    {"id": "lmstudio", "name": "LM Studio", "fmt": "GGUF and MLX",
     "surface": "Desktop app + `lms` CLI + server", "api": "OpenAI-compatible on :1234",
     "api_kind": "api", "repo": None, "lic": "Proprietary, free to use",
     "api_detail": {
         "endpoints": "OpenAI: /v1/models, /v1/chat/completions, /v1/completions, /v1/responses, /v1/embeddings. Its own REST API and TypeScript/Python SDKs are more capable than the compatibility layer.",
         "streaming": "Yes. Tool calls stream properly as `delta.tool_calls[].function.arguments` fragments you accumulate across chunks - the correct OpenAI shape.",
         "tools": "Standard OpenAI tool schemas, with per-family native formats and a documented generic fallback for models with no native tool support.",
         "structured": "`json_schema` only - **`json_object` mode is not supported**. Enforcement differs by engine: llama.cpp grammars for GGUF, Outlines for MLX. SDK integrations bind to Zod, Pydantic and msgspec.",
         "concurrency": "Serves multiple requests; models load and unload through the app or `lms`.",
         "gotcha": "The two engines are not equivalent through the same API. An open report has the MLX engine silently clamping context to 4864 tokens and ignoring every override, which surfaces as the model being bad rather than the server being wrong.",
     },
     "what": "App-first but not app-only. It ships both a llama.cpp engine and its own MLX engine, so "
             "for any given model it can take whichever path works, and its catalogue tends to carry a "
             "curated quant within a day of a release. The `lms` CLI and the server run headless."},
    {"id": "omlx", "name": "oMLX", "fmt": "MLX",
     "surface": "Menu-bar app + server", "api": "OpenAI and Anthropic",
     "api_kind": "api", "repo": "jundot/omlx", "lic": "Apache-2.0",
     "api_detail": {
         "endpoints": "OpenAI: /v1/chat/completions, /v1/completions, /v1/embeddings, /v1/rerank, /v1/models. Anthropic: /v1/messages, with adaptive thinking.",
         "streaming": "Yes, including `stream_options.include_usage`, and SSE keep-alives so a long prefill does not read-timeout the client. It also scales reported token counts so Claude Code's auto-compact triggers at the right moment on a smaller-context model.",
         "tools": "Per-family parsers (Qwen3.5 XML, GLM arg-key/value, MiniMax namespaced, Gemma, Kimi, Mistral, Longcat). **Tool calls do not stream incrementally** - assistant text streams while tool markup is suppressed, and structured calls are emitted only after the completed turn is parsed.",
         "structured": "JSON schema validation, plus MCP tool integration.",
         "concurrency": "Continuous batching, default 8 concurrent requests, over a hot/cold KV cache that spills to SSD and survives a restart.",
         "gotcha": "The two surfaces are not interchangeable in practice: there is an open report of the OpenAI endpoint returning 500 while the Anthropic endpoint on the same server works. A stricter channel check also drops valid gpt-oss calls addressed to `functions.*`.",
     },
     "what": "MLX serving built for agent clients: continuous batching, a hot/cold KV cache that spills "
             "blocks to SSD and survives a restart, and hand-written Metal kernels for the GLM-5.2, "
             "MiniMax M3 and Qwen3.5 families. Its LLM coverage is mlx-lm's, plus those kernels and its "
             "own additions - install the custom kernels or the affected families fall back silently to "
             "a much slower generic path."},
    {"id": "vllmmetal", "name": "vLLM Metal", "fmt": "MLX",
     "surface": "CLI + the standard vLLM server", "api": "OpenAI, via vLLM core",
     "api_kind": "api", "repo": "vllm-project/vllm-metal", "lic": "Apache-2.0",
     "api_detail": {
         "endpoints": "Whatever vLLM core exposes, because this is vLLM: /v1/chat/completions, "
                      "/v1/completions, /v1/embeddings, /v1/models, plus the pooling and rerank routes for "
                      "the embedding and reranker models it supports.",
         "streaming": "vLLM's own implementation rather than a reimplementation, so streaming, usage "
                      "accounting and the rest behave the way the upstream docs say they do.",
         "tools": "vLLM's tool parsers and guided decoding, again inherited from core. One live defect to "
                  "know about: mixed batches with top_k enabled on some requests and disabled on others "
                  "crash the Metal sampler.",
         "structured": "vLLM's guided decoding stack.",
         "concurrency": "Continuous batching and paged KV from vLLM core, over Metal kernels. Automatic "
                        "prefix caching is on by default for unified paged-KV models; hybrid GDN models "
                        "like Qwen3.8 must opt in with --enable-prefix-caching.",
         "gotcha": "Model coverage is far narrower than llama.cpp's - this is a young plugin with a "
                   "deliberately curated matrix, not a general loader. Check the supported-models table "
                   "before planning around it. Needs macOS 15+ and native arm64 Python 3.12 specifically. "
                   "And note the MLX pin is exact, not a floor: the prebuilt kernels link MLX private "
                   "headers and libmlx.dylib carries no SONAME version, so a wheel is only ABI-safe "
                   "against the one MLX it was built against. You cannot upgrade MLX underneath it.",
     },
     "what": "vLLM itself, running on Apple Silicon. This is a plugin in the vllm-project org that keeps "
             "vLLM core and swaps the compute layer for MLX, unifying MLX and PyTorch under one lowering "
             "path - so you get vLLM's scheduler, paged KV, continuous batching and API surface rather than "
             "a lookalike. Despite the name it is an MLX engine underneath: it pins a single exact MLX "
             "version, pulls in mlx-lm and mlx-vlm, and builds its Metal kernels as MLX primitives. Two things make it worth attention on new hardware: v0.2.0's unified paged varlen "
             "Metal kernel claims 83x TTFT and 3.6x throughput over v0.1.0, and as of August 2026 it uses "
             "the **M5 Neural Accelerator tensor units** to speed up MHA, GQA and MQA prefill - the only "
             "engine here that claims M5-specific acceleration. The cost is coverage: its model matrix is a "
             "curated list, not everything that exists."},
    {"id": "vllmmlx", "name": "vllm-mlx", "fmt": "MLX",
     "surface": "Server", "api": "OpenAI and Anthropic",
     "api_kind": "api", "repo": "waybarrios/vllm-mlx", "lic": "Apache-2.0",
     "api_detail": {
         "endpoints": "OpenAI: /v1/chat/completions, /v1/completions, /v1/embeddings, /v1/rerank, /v1/responses. Anthropic: /v1/messages with streaming, tool use and system prompts. Prometheus /metrics.",
         "streaming": "Yes on both surfaces. Usage is reported, but `cached_tokens` is not surfaced yet - an open PR - so you cannot see prefix-cache hits from the API.",
         "tools": "19 tool parsers (OpenAI, Anthropic, Gemini, Qwen, DeepSeek, Gemma and more) plus reasoning parsers selected with `--reasoning-parser`.",
         "structured": "`response_format` with `json_schema`.",
         "concurrency": "The strongest story on paper: continuous batching over a paged KV cache with prefix caching and SSD tiering, which is the whole reason the project exists.",
         "gotcha": "Three open defects land squarely on the streaming path: streamed tool calls can end without a `finish_reason`, closing a stream mid-flight leaves the generator and request state open, and a strict `json_schema` decode can wedge. Also bind carefully - non-loopback requests have been reported silently dropped on 0.0.0.0.",
     },
     "what": "A paged KV cache and continuous batching over mlx-lm's model classes. Unaffiliated with "
             "vllm-project/vllm despite the name. Because it wraps mlx-lm rather than reimplementing "
             "models, an architecture missing upstream is missing here, and mlx-lm's bugs arrive intact."},
    {"id": "mlxlm", "name": "mlx-lm", "fmt": "MLX",
     "surface": "CLI + `mlx_lm.server`", "api": "OpenAI-compatible, minimal",
     "api_kind": "api", "repo": "ml-explore/mlx-lm", "lic": "MIT",
     "api_detail": {
         "endpoints": "OpenAI: POST /v1/chat/completions (and bare /chat/completions), POST /v1/completions, GET /v1/models, GET /health. No embeddings, no rerank, no responses.",
         "streaming": "Yes, SSE, with `stream_options.include_usage` and `prompt_tokens_details` for cached prompt tokens.",
         "tools": "`tool_calls` are parsed and returned. It also implements `logprobs` and `top_logprobs` up to 11, which Ollama does not - a genuine inversion of the usual ordering.",
         "structured": "**None.** There is no `response_format`, no `json_schema` and no grammar support anywhere in the server. If your agent depends on constrained decoding, this engine cannot give it to you.",
         "concurrency": "A ThreadingHTTPServer over mlx-lm's BatchGenerator, but batching is switched off whenever a draft model is loaded or a `seed` is set - so speculative decoding and concurrency are mutually exclusive here.",
         "gotcha": "Better than its reputation on the basics and thinner than expected on structured output. Treat it as a correctness reference rather than a serving layer.",
     },
     "what": "Apple's own reference implementation, and the substrate almost everything MLX-shaped "
             "depends on. Treat it as the floor: an architecture with no model class here is absent from "
             "most of the MLX ecosystem at once. The bundled server is deliberately basic - one model, "
             "simple batching - so it is a correctness reference more than a serving layer."},
    {"id": "ds4", "name": "DwarfStar (ds4)", "fmt": "purpose-built GGUF",
     "surface": "CLI + ds4-server + built-in agent", "api": "OpenAI and Anthropic",
     "api_kind": "api", "repo": "antirez/ds4", "lic": "MIT",
     "api_detail": {
         "endpoints": "OpenAI: /v1/models, /v1/models/{alias}, /v1/chat/completions, /v1/completions, /v1/responses. Anthropic: /v1/messages. The model aliases are compatibility only - they all report whatever GGUF was passed with `-m`.",
         "streaming": "SSE on the chat, Responses and Anthropic surfaces, with `stream_options.include_usage`. In thinking mode reasoning streams on its own channel instead of being mixed into the final text, and the Responses surface emits the full Codex event lifecycle - `response.output_text.delta`, function-call argument events, and terminal `response.completed` / `incomplete` / `failed`.",
         "tools": "`tools` and `tool_choice` on all three surfaces. Schemas are rendered into DeepSeek's DSML format and generated calls mapped back. **Tool calls stream incrementally**: the header goes out as soon as the DSML invocation is recognised, then argument bytes are forwarded as `tool_calls[].function.arguments` deltas while generation continues.",
         "structured": "No `response_format` or grammar support; correctness comes from DSML canonicalisation rather than constrained decoding.",
         "concurrency": "`--batched-session N` preallocates N resident KV sessions with fair scheduling, and idle slots persist to the disk KV cache before reuse. MTP speculative decoding is disabled while native session batching is active.",
         "gotcha": "The best streaming implementation here, from the narrowest engine - but stateless clients have been reported failing to extend the live KV session on Flash/Metal, which quietly removes the prefix reuse that is the main reason to run it. Add `--cors` for browser clients; `--host 0.0.0.0` is opt-in.",
     },
     "what": "A single-purpose C and Metal engine for DeepSeek V4 Flash, DeepSeek V4 PRO and GLM-5.2 - "
             "deliberately not a general GGUF loader, so only the published checkpoints load. In exchange "
             "it gets a disk KV cache that persists sessions across restarts, resident session batching, "
             "SSD expert streaming for machines too small to hold the weights, and tensor parallelism "
             "across two Macs over Thunderbolt RDMA. Where it applies, it is the fastest option here."},
]

ENGINE_BY_ID = {e["id"]: e for e in ENGINES}

# Per-engine issue metadata: key -> (severity, headline, why it matters)
EMETA = {
    # ---------------- llama.cpp ----------------
    "ggml-org/llama.cpp#26965": ("critical", "DeepSeek V4 Flash tokenizer overflows its stack on long tool output",
        "An agent loop feeds tool results straight back into the prompt, so this is reachable on any run that "
        "reads a large file or a long test log. It takes the server down rather than returning an error."),
    "ggml-org/llama.cpp#25171": ("high", "DeepSeek V4 Flash 'forgets everything' mid-conversation",
        "Reported as context silently dropping earlier turns. On an agent that is the worst possible failure "
        "mode, because the run continues confidently on a truncated history rather than stopping."),
    "ggml-org/llama.cpp#25796": ("high", "DeepSeek V4 Flash errors out on tool calls with similar parameter names",
        "Tools that share parameter names - the normal case across a bundle of file and shell tools - can fail "
        "the whole request rather than one call."),
    "ggml-org/llama.cpp#25744": ("medium", "DeepSeek V4 Flash: 200 s prefill for a 10-token prompt",
        "A pathological cold-start path. Worth watching because a per-request fixed cost of that size makes "
        "short agent turns unusable even when steady-state decode is fine."),
    "ggml-org/llama.cpp#25751": ("high", "Sliding-window attention on Gemma 4 forgets key details",
        "Gemma 4's long context is built on SWA, so this bites exactly where the 256k window is the reason you "
        "picked the model. Quality loss, not a crash, which makes it harder to notice."),
    "ggml-org/llama.cpp#25522": ("medium", "Gemma 4 crashes with MTP speculative decoding",
        "MTP is the reason to prefer the GGUF build - the checkpoint ships a draft head. With MTP off the model "
        "runs, so this costs speed rather than correctness."),
    "ggml-org/llama.cpp#25739": ("medium", "Google's own Gemma 4 QAT GGUF aborts at vocab load",
        "Filed against the E2B variant. Relevant because the QAT repo is the recommended download, so a vocab "
        "assert there affects the default path rather than an exotic one."),
    "ggml-org/llama.cpp#27335": ("high", "Qwen3.8-27B crashes on an M2 Ultra with default settings",
        "Confirmed on Darwin arm64 with the Metal backend, and on defaults rather than a tuned command line - "
        "the one class of bug that hits you on first run."),
    "ggml-org/llama.cpp#27139": ("medium", "Qwen3.8 tool-calling errors resolved by substituting the Qwen3.6 chat template",
        "The shipped template mis-renders something in the tool path. A workaround exists and is a single "
        "`--chat-template-file`, but until it is fixed the default template is wrong for agent use."),
    "ggml-org/llama.cpp#26382": ("medium", "Same K and V cache type enforced for models with no V cache",
        "GLM-5.2's DSA attention has no V cache to quantise, but the flag pair is validated as if it did, so you "
        "cannot set the K type independently. Costs memory on the model that has the least to spare."),
    "ggml-org/llama.cpp#27141": ("high", "nemotron_h_moe aborts in ggml_ssm_scan during context reservation",
        "Fires at context reservation, before any token is generated, and the assertion is in the shared SSM "
        "scan rather than a backend - so it is not a CUDA-only report."),
    "ggml-org/llama.cpp#27066": ("low", "Adaptive-P sampling is broken on Muse Glimmer",
        "A sampler, not the model. Pin top-p explicitly and it is a non-issue; listed because the default "
        "sampler config is what most launchers use."),
    "ggml-org/llama.cpp#27427": ("high", "A ~50 KB request crashes llama-server with exit 139",
        "Filed on Glimmer. 50 KB is an ordinary agent turn once a file or a diff is in the prompt, and the "
        "process dies rather than rejecting the request."),
    "ggml-org/llama.cpp#26894": ("medium", "DFlash drafter fails to bind when the GGUF encodes attention.sliding_window",
        "Blocks speculative decoding on exactly the builds that carry a sliding-window key. The target model "
        "still runs; you lose the draft head's speedup."),
    "ggml-org/llama.cpp#25967": ("high", "Duplicate GBNF rules with a large tool list break grammar parsing",
        "Constrained decoding is how tool calls are kept well-formed. Past some number of tools the generated "
        "grammar fails to parse - which is to say the failure arrives as you add capability to your agent."),
    "ggml-org/llama.cpp#27720": ("medium", "gpt-oss malformed Harmony channel headers break tool calls",
        "gpt-oss encodes reasoning and tool calls in Harmony channels; a garbled header drops the call. Model "
        "specific and parser-side, so it is fixable without touching the weights."),
    "ggml-org/llama.cpp#26365": ("low", "Kimi K3 full-size vision lives on a branch, not master",
        "The text backbone is in mainline. This asks for tensor-split support on the vision branch, which is a "
        "useful signal about how finished K3 support is rather than a blocker for text work."),

    "ggml-org/llama.cpp#27428": ("low", "draft-mtp roughly halves prompt processing on a multi-GPU layer split",
        "Multi-GPU only - a single GPU is fine, so this does not apply to a Mac. Listed because it is the most "
        "active MTP thread and the fix will touch the shared path."),
    "jundot/omlx#2691": ("low", "Request: an oQ4e-mtp quantisation of Qwen3.8-27B",
        "oMLX's own quant format with the MTP head merged. Until it exists you are running a generic "
        "mlx-community build rather than one tuned for this server."),
    "ggml-org/llama.cpp#27741": ("high", "Feature request: support Qwen3.8-Flash-Next",
        "The whole blocker for this model. Its config reports `qwen4_exp` - a preview of the Qwen4 "
        "architecture - and no runtime on this page implements it yet. Watch this thread rather than the quant "
        "repositories."),
    "ggml-org/llama.cpp#27727": ("medium", "Garbled output from a Qwen3-Coder-Next abliterated GGUF",
        "Filed against a community abliterated finetune rather than the base weights, so it may say more about "
        "that conversion than about the architecture. Worth knowing before you blame the model."),
    # ---------------- vLLM Metal ----------------
    "vllm-project/vllm-metal#646": ("high", "Mixed batches with top_k enabled on some requests crash the Metal sampler",
        "Continuous batching means requests with different sampling parameters land in the same batch, so "
        "this is reachable with ordinary mixed traffic rather than an exotic configuration."),
    "vllm-project/vllm-metal#482": ("medium", "Draft-model speculative decoding is net-negative",
        "Each request re-ingests the full prompt into the draft model, which costs more than the draft saves. "
        "Worth knowing before you reach for spec decode here; the built-in MTP path (#610) is the one to watch."),
    "vllm-project/vllm-metal#610": ("medium", "Built-in MTP draft heads do not yet work with prefix caching on hybrid GDN",
        "Qwen3.8 is exactly that shape, and it ships an MTP head. Until this lands you choose between the "
        "draft head and the prefix cache rather than having both."),
    "vllm-project/vllm-metal#644": ("medium", "Nemotron-H (Mamba-2 + MoE hybrid) paged attention not implemented",
        "Open request rather than a bug. It is the reason Nemotron 3.5 Lightning does not load here."),
    "vllm-project/vllm-metal#450": ("low", "RFC: attention backend dispatch",
        "Design work on how backends get selected per model. Useful for judging how settled the internals are."),
    "vllm-project/vllm-metal#360": ("medium", "RFC: a specialised Metal kernel for MLA paged attention",
        "Until this exists, latent-attention models fall back to MLX SDPA with no Metal kernel - which is why "
        "the GLM-4.5 row in the support matrix is flagged as slow and untested."),
    # ---------------- oMLX ----------------
    "jundot/omlx#3121": ("high", "DeepSeek V4 Flash decodes at 4-17 tok/s on an M5 Max from residency thrash",
        "Traced to the bundled mlx 0.32.0 keeping a single residency set, so the weights fault instead of "
        "staying wired. A fix is identified in the thread; until it ships, expect a fraction of the speed ds4 "
        "gets on the same machine."),
    "jundot/omlx#2469": ("high", "DeepSeek V4 mxfp4 gather_qmm_blocks crashes on float32 activations",
        "MXFP4 is the quantisation DeepSeek actually released, so this is the preferred build rather than a "
        "fringe one."),
    "jundot/omlx#2606": ("medium", "Thinking leaks into content when generation is truncated mid-thought",
        "A truncated turn returns reasoning as if it were the answer. Downstream that is indistinguishable "
        "from the model answering badly, and it corrupts anything that parses the reply."),
    "jundot/omlx#2493": ("medium", "'Cache signature mismatch' then a severe performance drop on DeepSeek V4",
        "The prefix cache silently stops being used, so every turn re-prefills. On long agent conversations "
        "that is the difference between seconds and minutes per turn."),
    "jundot/omlx#3006": ("high", "GLM-5.2 prefill far below published figures on an M3 Ultra 512 GB",
        "The published 845 tok/s number depends on the native DSA kernels being compiled in. This thread is "
        "where you find out whether your install actually has them - the fallback is roughly 30x slower and "
        "uses more memory."),
    "jundot/omlx#2099": ("high", "GLM-5.2 loops",
        "Repetition loops on the flagship model. A loop burns the context window and the wall clock without "
        "producing a turn, which on a metered agent is worse than an error."),
    "jundot/omlx#1927": ("medium", "GLM-5.2-mxfp4 will not load",
        "Filed against 0.4.4. Matters because mxfp4 is the smallest faithful GLM-5.2 build, and the alternative "
        "affine quants are larger at the same nominal bit width."),
    "jundot/omlx#2208": ("medium", "GLM-5.2 cold prefill throttles near the memory ceiling",
        "GLM-5.2 leaves very little headroom on any Mac that can hold it, so the adaptive throttle engages in "
        "normal use rather than at an extreme."),
    "jundot/omlx#1968": ("high", "MiniMax-M3 fails to load: 2225 parameters not in model (vision_tower)",
        "The released checkpoint is `minimax_m3_vl` - a vision-language model - and the text path rejects the "
        "vision tower's tensors instead of skipping them."),
    "jundot/omlx#1862": ("medium", "MiniMax 3 model-type error",
        "The `minimax_m3_vl` model type is not mapped cleanly. Same root cause as the loader failure above, "
        "seen from the config side."),
    "jundot/omlx#2590": ("medium", "Scope clarification: MiniMax M3 long-prefill fixes across Q4 and oQ3",
        "An open question about which quant tiers the long-prefill fixes cover. Read it before choosing a "
        "MiniMax quant, because the answer decides whether long prompts work."),
    "jundot/omlx#2747": ("high", "Qwen3.8-27B single-stream decode regressed 36.5 to 24 tok/s on an M3 Ultra",
        "A third of decode throughput, on the model most people will try first, with the MTP path implicated. "
        "This is the number to check against before assuming an MLX server beats llama.cpp here."),
    "jundot/omlx#2854": ("medium", "No continuous-batching results published for Qwen3.8 and DFlash2",
        "Continuous batching is the reason to run a server instead of the CLI. Unmeasured on this architecture "
        "means the concurrency story is unproven, not that it is broken."),
    "jundot/omlx#3117": ("medium", "Qwen3.8 with the Neural Engine enabled produces zero tokens",
        "ANE offload is off by default, so this is an opt-in trap rather than a first-run one - but it is silent, "
        "returning an empty completion rather than an error."),
    "jundot/omlx#2972": ("medium", "Process-global Qwen patches contaminate a resident engine after loading another model",
        "Multi-model serving is a headline oMLX feature; this is the cross-contamination it can cause. The "
        "second model loads and the first one quietly changes behaviour."),
    "jundot/omlx#2589": ("high", "Muse Glimmer oQ4e: tool calling broken and decode slow",
        "Tool calling is the whole point of Glimmer - it leads MCP Atlas. Traced to a pre-#1839 quantisation, so "
        "check which build you pulled before concluding the model is bad."),
    "jundot/omlx#2600": ("high", "DFlash speculative decoding renders the cache non-functional on Gemma and Glimmer",
        "Turning on the draft head disables the prefix cache, so you trade a decode speedup for full re-prefill "
        "every turn. On agent workloads that is a net loss."),
    "jundot/omlx#2604": ("medium", "Glimmer DFlash can end a turn after reasoning without the forced tool call",
        "The model finishes its reasoning and stops instead of emitting the call. An agent sees a turn that did "
        "nothing, which usually gets retried - so it costs two turns, not one."),
    "jundot/omlx#2641": ("medium", "Glimmer is extremely slow with DFlash on",
        "The companion report to the two above: on this family the draft head currently costs more than it "
        "saves. Run Glimmer without it."),
    "jundot/omlx#2786": ("medium", "Gemma 4 performance regressed after 0.6.1",
        "A version-pinning matter rather than an architecture one, but it means the newest build is not "
        "automatically the right one for this model."),
    "jundot/omlx#1794": ("medium", "Hitting the context wall with Gemma 4",
        "Gemma 4 advertises 256k. This is where users find the practical ceiling on a Mac, which is set by KV "
        "residency rather than by the model."),
    "jundot/omlx#2216": ("high", "Legitimate gpt-oss tool calls with explicit to=functions.* are dropped",
        "A regression from a stricter channel check. Calls that are correctly formed per the Harmony spec get "
        "discarded, so the agent sees a turn with no action."),
    "jundot/omlx#2018": ("medium", "OpenAI endpoint returns 500 while the Anthropic endpoint works",
        "Both endpoints front the same engine, so a client that speaks Anthropic gets a working server and a "
        "client that speaks OpenAI does not. Worth knowing which one your agent uses."),
    "jundot/omlx#1195": ("low", "MTP speculative decoding not yet supported for Nemotron-H",
        "A feature request. Nemotron 3.5 Lightning ships MTP weights, so this is speed left on the table rather "
        "than anything broken."),
    "jundot/omlx#2307": ("high", "A model-discovery race orphans a loaded engine - 404 GB unreclaimable, restart only",
        "Server-wide, not per model. Discovery racing an in-flight load leaks the whole resident model; on a "
        "256 GB machine that is the entire budget gone until you restart."),
    "jundot/omlx#2137": ("medium", "GLM-5.2-mxfp4 prefill fell from 160-180 tok/s to 40 tok/s on 0.5.0.dev2",
        "Closed as completed in July 2026, with memory also fluctuating between 400 and 520 GB on a 512 GB M3 "
        "Ultra. Kept on the list as the reference point for what a healthy GLM-5.2 prefill looks like, and as a "
        "reminder that a version bump can cost you a factor of four on this model."),
    "ml-explore/mlx-lm#1192": ("high", "The DeepSeek V4 port thread",
        "Where the community port was developed and tested before PR #1233. Useful for finding out what already "
        "works in a fork if you do not want to wait for the merge."),
    "waybarrios/vllm-mlx#699": ("high", "DFlash and DSpark draft heads block speculative decoding",
        "Both are the vendor-shipped draft mechanisms on the models that have one. If neither is wired up, "
        "speculative decoding on this engine is limited to what the generic k=1 path gives you."),

    # ---------------- ds4 / DwarfStar ----------------
    "antirez/ds4#853": ("high", "BPE merge loop is O(n squared): large prompts take minutes to tokenize",
        "Tokenization is pure fixed cost before any GPU work. An agent that pastes a file into the prompt pays "
        "it on every turn, and it does not show up in the tok/s figures."),
    "antirez/ds4#816": ("high", "Stateless chat clients never extend the live KV session on Flash/Metal",
        "Most agent clients are stateless - they resend a longer prompt each turn. If the session is not "
        "extended, the disk KV cache and prefix reuse stop paying, which is the main reason to run ds4."),
    "antirez/ds4#845": ("high", "--layers maps a shard as N disjoint Metal buffers, about 77x slower decode",
        "Hits the distributed path specifically. If you are splitting DeepSeek V4 PRO or GLM-5.2 across two "
        "Macs, this is the first thing to check when the numbers look impossible."),
    "antirez/ds4#836": ("medium", "Possible ds4-server memory leak",
        "Unconfirmed. On a machine where the model already occupies most of RAM, a slow server-side leak ends "
        "as an OOM rather than as swap."),
    "antirez/ds4#807": ("medium", "DeepSeek V4 PRO 0813 support",
        "The 0813 refresh is not yet a supported checkpoint. ds4 is deliberately narrow, so a newer PRO release "
        "is a tracked task rather than something that just loads."),
    "antirez/ds4#805": ("medium", "Disk KV cache can be reused across different weights sharing a model_id",
        "Swap quantisations and the cache from the old weights can be restored against the new ones. Silent "
        "wrong-context, and it survives a restart because that is what the disk cache is for."),
    "antirez/ds4#851": ("low", "DeepSeek V4 Flash vision is not supported",
        "Text only today. Irrelevant for coding and terminal work; relevant if you wanted the same engine for "
        "screenshots."),
    "antirez/ds4#839": ("low", "No tagged releases, which blocks downstream packaging",
        "You build from a moving main branch. The project describes itself as beta and fast-changing, so pin a "
        "commit yourself if you care about reproducibility."),
    "antirez/ds4#860": ("medium", "ds4 crashes the machine on launch for one reporter",
        "A single report without a resolved cause. Listed because a full-machine crash is a different risk "
        "class from a process crash."),

    # ---------------- mlx-lm, engine-scoped ----------------
    "ml-explore/mlx-lm#1233": ("critical", "PR: DeepSeek V4 model class, still open",
        "This is the entire MLX blocker for DeepSeek V4. Until it merges there is no `deepseek_v4` in mlx-lm, so "
        "no MLX server that wraps mlx-lm can load the architecture no matter which quant you download."),
    "ml-explore/mlx-lm#1281": ("medium", "Request: add DeepSeek V4 to mlx_lm",
        "The demand-side thread for the PR above. Useful as a temperature check on whether the port is moving."),
    "ml-explore/mlx-lm#1404": ("medium", "DeepSeek V4 Flash drifts from Simplified to Traditional Chinese",
        "Filed against the mlx-vlm DeepSeek path, which is the only working MLX route today. A quality defect "
        "rather than a load failure, and confined to CJK output."),
    "ml-explore/mlx-lm#1662": ("high", "Models that discard update_and_fetch's return leak one Metal buffer per layer per generation",
        "The general form of the DeepSeek V4 residency growth. Any model class written with that mistake leaks "
        "for as long as the process lives, so it shows up as a long-run failure, not a first-run one."),
    "ml-explore/mlx-lm#1335": ("high", "Tool calls dropped when the tokenizer merges the tool-call start marker",
        "The json_tools parser never matches, so the call is returned as plain text. Architecture-independent "
        "and specific to agent use."),
}

# ---------------------------------------------------------------------------
# The matrix. Per cell:
#   s     status: works | degraded | blocked | none
#   label tab pill text
#   w     resident weight in GB for the fit maths on that engine (None = no weights)
#   q     (label, optional HF repo) for the build the weight refers to
#   note  what running it on this engine is actually like
#   items issue keys, resolved against EMETA and the global META
# ---------------------------------------------------------------------------

def cell(s, label, w, q, note, items=()):
    return {"s": s, "label": label, "w": w, "q": q, "note": note, "items": list(items)}


MATRIX = {
    # ================================================================ GLM-4.7
    "glm47": {
        "llamacpp": cell("works", "Runs", 158.7,
            ("GLM-4.7-UD-Q3_K_XL, 4 shards", "unsloth/GLM-4.7-GGUF"),
            "The best fit of any engine for this model, because llama.cpp has quant tiers MLX does not. "
            "UD-Q3_K_XL is 158.7 GB against the MLX 4-bit's 198.6 GB, which turns a 21 GB KV budget into "
            "about 60 GB on the same machine - the difference between a demo and a working context. IQ4_XS "
            "(191.6 GB) and UD-Q4_K_XL (204.6 GB) sit either side of the MLX build if you would rather spend "
            "the memory on weights. No open GLM-4.7-specific Metal issues.",
            []),
        "ollama": cell("works", "Runs", 204.6,
            ("glm-4.7, library default tag", None),
            "`ollama run glm-4.7` works, but the default tag is a Q4-class build near 205 GB, which leaves "
            "almost nothing for KV on a 256 GB machine. Pull an explicit smaller tag rather than the default "
            "if you are on one box. Note that on Apple Silicon Ollama now routes through MLX by default, so "
            "which path you get depends on what the tag ships.",
            []),
        "lmstudio": cell("works", "Runs", 158.7,
            ("either engine; GGUF tiers are the reason to use it", "bartowski/zai-org_GLM-4.7-GGUF"),
            "The one engine that can pick per model: load the GGUF Q3 tier for headroom or the mlx-community "
            "4-bit for speed, from the same app, and compare them without changing tools. Serves on :1234 for "
            "any OpenAI client.",
            []),
        "omlx": cell("works", "Runs", 198.6,
            ("mlx-community/GLM-4.7-4bit, 39 shards", "mlx-community/GLM-4.7-4bit"),
            "glm4_moe is a mature mlx-lm path and oMLX's GLM tool parser is explicitly implemented, so this is "
            "a comfortable pairing - you get continuous batching and the SSD KV tier on top. The constraint is "
            "arithmetic, not software: 198.6 GB of weights on a 256 GB box leaves about 21 GB for KV, and the "
            "SSD cold tier is what makes that survivable.",
            ["jundot/omlx#2307"]),
        "vllmmlx": cell("works", "Runs", 198.6,
            ("mlx-community/GLM-4.7-4bit, 39 shards", "mlx-community/GLM-4.7-4bit"),
            "The original recommendation on this page and still a good one. glm4_moe has zero open issues in "
            "mlx-lm - every one closed - and it uses conventional attention rather than hybrid linear "
            "attention, so it should sidestep the prefix-cache bug that cripples Qwen3.8-27B on this engine. "
            "Confirm that first; it is the main reason to prefer it here.",
            ["waybarrios/vllm-mlx#725"]),
        "mlxlm": cell("works", "Runs", 198.6,
            ("mlx-community/GLM-4.7-4bit, 39 shards", "mlx-community/GLM-4.7-4bit"),
            "Loads and generates. Use it to establish what the model does correctly before adding a serving "
            "layer, then move to one of the servers above for concurrency.",
            ["ml-explore/mlx-lm#1335"]),
        "vllmmetal": cell("blocked", "Blocked", None, None,
            "The support matrix lists GLM-4.7-Flash but not the full 358B model, and the GLM-4.5 row it does "
            "carry is flagged as MLA with no Metal kernel and untested. This is a curated matrix rather "
            "than a general loader, so absence means absence.",
            ['vllm-project/vllm-metal#360']),
        "ds4": cell("none", "Out of scope", None, None,
            "ds4 loads DeepSeek V4 Flash, DeepSeek V4 PRO and GLM-5.2 only. GLM-4.7 is a different "
            "architecture and will not load.", []),
    },

    # ========================================================== GLM-4.7-Flash
    "glm47f": {
        "llamacpp": cell("works", "Runs", 18.2,
            ("GLM-4.7-Flash-Q4_K, single file", "ggml-org/GLM-4.7-Flash-GGUF"),
            "First-class: the GGUF lives in ggml-org's own namespace, which is as strong a support signal as "
            "this ecosystem gives. 18.2 GB at Q4_K, 31.8 GB at Q8_0, and enough headroom on any machine here "
            "that quantisation choice is about quality rather than fit.",
            []),
        "ollama": cell("works", "Runs", 18.2, ("glm-4.7-flash", None),
            "`ollama run glm-4.7-flash`. The easiest thing on this page to get running, and small enough that "
            "the default tag is the right tag.", []),
        "lmstudio": cell("works", "Runs", 16.9,
            ("MLX 4-bit or GGUF Q4_K", "lmstudio-community/GLM-4.7-Flash-MLX-8bit"),
            "Curated in both formats under lmstudio-community, MLX at 6-bit and 8-bit included. A good place to "
            "measure what the MLX-versus-GGUF gap actually is on your machine, since both builds are one click "
            "apart.", []),
        "omlx": cell("works", "Runs", 16.9,
            ("mlx-community/GLM-4.7-Flash-4bit, 4 shards", "mlx-community/GLM-4.7-Flash-4bit"),
            "The best match on this page for what oMLX is for. 3B active makes decode cheap, 16.9 GB leaves the "
            "rest of the machine for KV blocks, and continuous batching plus the hot/cold cache is exactly the "
            "shape of a high-concurrency cheap tier.",
            ["jundot/omlx#2307"]),
        "vllmmlx": cell("works", "Runs", 16.9,
            ("mlx-community/GLM-4.7-Flash-4bit, 4 shards", "mlx-community/GLM-4.7-Flash-4bit"),
            "3B active, so decode is bandwidth-cheap and KV space is abundant - the opposite tradeoff to "
            "GLM-4.7 on the same mature code path and quant family.",
            ["waybarrios/vllm-mlx#725"]),
        "mlxlm": cell("works", "Runs", 16.9,
            ("mlx-community/GLM-4.7-Flash-4bit, 4 shards", "mlx-community/GLM-4.7-Flash-4bit"),
            "Works, and small enough that the CLI is a reasonable way to use it rather than just to test it.",
            ["ml-explore/mlx-lm#1335"]),
        "vllmmetal": cell("works", "Runs, experimental", None, None,
            "Experimental but on the plain GQA paged path with automatic prefix caching, and "
            "`mlx-community/GLM-4.7-Flash-4bit` is the matrix's own example checkpoint. 3B active over "
            "vLLM's continuous batching is a good pairing.",
            ['vllm-project/vllm-metal#646']),
        "ds4": cell("none", "Out of scope", None, None,
            "Not one of the three checkpoints ds4 loads.", []),
    },

    # ====================================================== Muse Glimmer 30B
    "glimmer": {
        "llamacpp": cell("works", "Runs", 16.8,
            ("Muse-Glimmer-30B-KQuant-17GB-Q4_K_M", "meta-models/Muse-Glimmer-30B-GGUF"),
            "Meta publishes the GGUF itself, alongside an mmproj for vision and a 1.6 GB dflash draft head for "
            "speculative decoding. Two caveats that both matter for agents: a roughly 50 KB request has been "
            "reported to kill llama-server outright, and the draft head fails to bind on builds that encode a "
            "sliding-window key.",
            ["ggml-org/llama.cpp#27427", "ggml-org/llama.cpp#26894", "ggml-org/llama.cpp#27066"]),
        "ollama": cell("works", "Runs", 17.0, ("muse-glimmer", None),
            "In the library with a full tag ladder from 17 GB to 57 GB. Nothing model-specific to work around.",
            []),
        "lmstudio": cell("works", "Runs", 16.8,
            ("GGUF or MLX, both curated", "lmstudio-community/Muse-Glimmer-30B-GGUF"),
            "Curated in both formats. Given that the MLX path has live tool-calling and speculative-decoding "
            "reports and the GGUF path does not, being able to switch engines without changing tools is worth "
            "something here.", []),
        "omlx": cell("degraded", "Runs, degraded", 19.4,
            ("mlx-community/Muse-Glimmer-30B-4bit, 4 shards", "mlx-community/Muse-Glimmer-30B-4bit"),
            "It loads and it is fast in principle, but the open reports cluster on precisely what you would buy "
            "Glimmer for. Tool calling has been reported broken on the oQ4e checkpoint, and DFlash speculative "
            "decoding both disables the prefix cache and can end a turn after reasoning without emitting the "
            "forced call. Run it with DFlash off and check which quant you pulled.",
            ["jundot/omlx#2589", "jundot/omlx#2600", "jundot/omlx#2604", "jundot/omlx#2641"]),
        "vllmmlx": cell("works", "Runs", 19.4,
            ("mlx-community/Muse-Glimmer-30B-4bit, 4 shards", "mlx-community/Muse-Glimmer-30B-4bit"),
            "A clean pairing: zero open muse_glimmer issues in mlx-lm, a full mlx-community quant family at "
            "4/5/6/8-bit, and a dense 30B that needs none of the hybrid-attention machinery that breaks "
            "elsewhere on this engine.", []),
        "mlxlm": cell("works", "Runs", 19.4,
            ("mlx-community/Muse-Glimmer-30B-4bit, 4 shards", "mlx-community/Muse-Glimmer-30B-4bit"),
            "muse_glimmer has no open issues in mlx-lm. This is the quiet reference path for the model.",
            ["ml-explore/mlx-lm#1335"]),
        "vllmmetal": cell("blocked", "Blocked", None, None,
            "Not in the support matrix. The project asks that unsupported models be raised as issues rather "
            "than assumed, which is a reasonable read on how narrow the tested set is.",
            []),
        "ds4": cell("none", "Out of scope", None, None, "Not one of the three checkpoints ds4 loads.", []),
    },

    # ================================================ Nemotron 3.5 Lightning
    "nemolight": {
        "llamacpp": cell("degraded", "Runs, degraded", 18.9,
            ("NVIDIA-Nemotron-3.5-Lightning-30B-A3B-Q4_0", "ggml-org/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-GGUF"),
            "ggml-org publishes it, with separate MTP draft weights at Q4/Q8/BF16 so speculative decoding is "
            "available. The catch is `nemotron_h_moe` aborting inside ggml_ssm_scan during context reservation - "
            "before generation starts, in the shared SSM kernel rather than a backend-specific path. Check that "
            "issue against your build before committing to this one.",
            ["ggml-org/llama.cpp#27141"]),
        "ollama": cell("works", "Runs", 18.9, ("nemotron-3.5-lightning", None),
            "In the library. The simplest route to trying the model, and at 3B active it is cheap to leave "
            "running.", []),
        "lmstudio": cell("works", "Runs", 17.8,
            ("GGUF or MLX 4-bit", "lmstudio-community/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-GGUF"),
            "Curated GGUF plus the mlx-community 4-bit. Given the llama.cpp SSM assertion above, having the MLX "
            "path a click away is the practical value here.", []),
        "omlx": cell("works", "Runs", 17.8,
            ("mlx-community/...Lightning-30B-A3B-4bit, 4 shards",
             "mlx-community/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-4bit"),
            "Loads on the nemotron_h path with nothing architecture-level open against it. MTP is not wired up "
            "yet, so the draft weights NVIDIA shipped go unused - speed left on the table rather than a defect.",
            ["jundot/omlx#1195"]),
        "vllmmlx": cell("works", "Runs", 17.8,
            ("mlx-community/...Lightning-30B-A3B-4bit, 4 shards",
             "mlx-community/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-4bit"),
            "3B active makes this the cheapest thing here to run at concurrency, and nothing for this "
            "architecture is open in mlx-lm.", []),
        "mlxlm": cell("works", "Runs", 17.8,
            ("mlx-community/...Lightning-30B-A3B-4bit, 4 shards",
             "mlx-community/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-4bit"),
            "Runs on the hybrid Mamba-Transformer path without special handling.", []),
        "vllmmetal": cell("blocked", "Blocked", None, None,
            "Nemotron-H paged attention is an open request - the Mamba-2 plus MoE hybrid has no "
            "implementation here yet. That issue is the thing to watch.",
            ['vllm-project/vllm-metal#644']),
        "ds4": cell("none", "Out of scope", None, None, "Not one of the three checkpoints ds4 loads.", []),
    },

    # =========================================================== gpt-oss-120b
    "gptoss": {
        "llamacpp": cell("degraded", "Runs, degraded", 63.4,
            ("gpt-oss-120b-MXFP4, single file", "ggml-org/gpt-oss-120b-GGUF"),
            "63.4 GB in OpenAI's native MXFP4, from ggml-org, plus an EAGLE3 draft model. It runs well; both "
            "open problems are in the agent path rather than the model. A large tool list can generate a GBNF "
            "grammar that fails to parse, and malformed Harmony channel headers drop tool calls.",
            ["ggml-org/llama.cpp#25967", "ggml-org/llama.cpp#27720"]),
        "ollama": cell("works", "Runs", 63.4, ("gpt-oss:120b", None),
            "`ollama run gpt-oss:120b`. One of the better-exercised models in the library.", []),
        "lmstudio": cell("works", "Runs", 63.4,
            ("MXFP4 GGUF or MLX 4-bit", "lmstudio-community/gpt-oss-120b-GGUF"),
            "Curated in both formats. 5.1B active keeps decode fast on either engine.", []),
        "omlx": cell("degraded", "Runs, degraded", 65.8,
            ("mlx-community/gpt-oss-120b-4bit, 13 shards", "mlx-community/gpt-oss-120b-4bit"),
            "Loads comfortably - 65.8 GB leaves plenty of KV room - but the Harmony plumbing has open defects "
            "that specifically cost tool calls: correctly-formed calls addressed to `functions.*` have been "
            "dropped by a stricter channel check, and there is a report of the OpenAI endpoint 500ing while the "
            "Anthropic endpoint on the same server works.",
            ["jundot/omlx#2216", "jundot/omlx#2018"]),
        "vllmmlx": cell("works", "Runs", 65.8,
            ("mlx-community/gpt-oss-120b-4bit, 13 shards", "mlx-community/gpt-oss-120b-4bit"),
            "A genuinely comfortable fit: 5.1B active means fast decode, 65.8 GB leaves plenty of KV room, and "
            "the gpt_oss path in mlx-lm is quiet.", []),
        "mlxlm": cell("works", "Runs", 65.8,
            ("mlx-community/gpt-oss-120b-4bit, 13 shards", "mlx-community/gpt-oss-120b-4bit"),
            "Quiet on the model side. Harmony parsing is the client's problem here rather than the engine's.",
            []),
        "vllmmetal": cell("works", "Runs, experimental", None, None,
            "Listed as experimental, with a dedicated sink-attention kernel and automatic prefix caching. "
            "gpt-oss is a shape that trips several engines on this page, so a purpose-built attention path "
            "for it is worth something.",
            ['vllm-project/vllm-metal#646']),
        "ds4": cell("none", "Out of scope", None, None, "Not one of the three checkpoints ds4 loads.", []),
    },

    # ============================================================ Gemma 4 31B
    "gemma4": {
        "llamacpp": cell("works", "Runs", 17.7,
            ("gemma-4-31B_q4_0-it, Google's own QAT GGUF", "google/gemma-4-31B-it-qat-q4_0-gguf"),
            "This is the model the MLX-only view of the world gets most wrong. Google publishes a "
            "quantisation-aware-trained q4_0 GGUF itself - 17.7 GB, plus a 1.2 GB mmproj for vision - so the "
            "recommended download comes from the model's own authors and QAT means less quality lost than a "
            "post-hoc 4-bit. Two things to know: sliding-window attention has a report of dropping earlier "
            "context, which matters because SWA is how the 256k window is built, and MTP speculative decoding "
            "crashes today.",
            ["ggml-org/llama.cpp#25751", "ggml-org/llama.cpp#25522", "ggml-org/llama.cpp#25739"]),
        "ollama": cell("works", "Runs", 17.7, ("gemma4", None),
            "`ollama run gemma4`, with a tag ladder from 10 GB to 24 GB. The single easiest way to get the "
            "highest tool-use score on this page running on a Mac.", []),
        "lmstudio": cell("works", "Runs", 17.7,
            ("gemma-4-31B-it-QAT-GGUF", "lmstudio-community/gemma-4-31B-it-QAT-GGUF"),
            "The QAT build is curated under lmstudio-community. Since no 4-bit MLX quant of the 31B exists, LM "
            "Studio's GGUF engine is the path here, not its MLX one.", []),
        "omlx": cell("degraded", "Runs, degraded", 17.5,
            ("no 4-bit MLX quant of the 31B; smaller Gemma 4 variants only", None),
            "oMLX has real Gemma 4 traffic - a Gemma tool parser, and open reports of a post-0.6.1 performance "
            "regression, a practical context wall well short of the advertised 256k, and DFlash disabling the "
            "prefix cache. But the specific problem for the 31B is upstream: mlx-community publishes no 4-bit "
            "quant of it, only a bf16 drafter and a 12B coder finetune, so you would be converting it yourself "
            "against an mlx-lm path that has more open issues than any other architecture tracked here.",
            ["jundot/omlx#2786", "jundot/omlx#1794", "jundot/omlx#2600",
             "ml-explore/mlx-lm#1493", "ml-explore/mlx-lm#1352"]),
        "vllmmlx": cell("blocked", "Blocked", 17.5,
            ("no 4-bit MLX quant published for the 31B", None),
            "The worst MLX story on the page. No 4-bit quant of the 31B to load, and gemma4 carries more open "
            "mlx-lm issues than any other architecture here: generation hangs after prompt processing, empty "
            "content when thinking is on, a variant that is not recognised at all, and RotatingKVCache "
            "quantisation not implemented.",
            ["ml-explore/mlx-lm#1493", "ml-explore/mlx-lm#1352", "ml-explore/mlx-lm#1242",
             "waybarrios/vllm-mlx#590", "ml-explore/mlx-lm#1573"]),
        "mlxlm": cell("blocked", "Blocked", 17.5,
            ("no 4-bit MLX quant published for the 31B", None),
            "Same blockers, one layer down. These are the issues every MLX server inherits.",
            ["ml-explore/mlx-lm#1493", "ml-explore/mlx-lm#1352", "ml-explore/mlx-lm#1242",
             "ml-explore/mlx-lm#1573"]),
        "vllmmetal": cell("works", "Runs", None, None,
            "Fully supported, with a Metal kernel for its per-layer sliding window and YOCO, and automatic "
            "prefix caching on by default rather than opt-in. That makes this the cleanest MLX route to "
            "Gemma 4 by a distance - mlx-lm cannot load the 31B at all. The example checkpoint in the "
            "matrix is the small E2B variant, so verify the 31B before planning around it.",
            []),
        "ds4": cell("none", "Out of scope", None, None, "Not one of the three checkpoints ds4 loads.", []),
    },

    # =========================================================== Qwen3.8-27B
    "qwen38": {
        "llamacpp": cell("works", "Runs", 17.6,
            ("Qwen3.8-27B-UD-Q4_K_XL + 1.4 GB MTP draft", "unsloth/Qwen3.8-27B-GGUF"),
            "The better path for this model, for one specific reason: the GGUF repo ships a separate 1.4 GB MTP "
            "draft head, so `--draft-mtp` gives you real multi-token speculative decoding - exactly the thing "
            "that is capped at k=1 on the MLX servers. A 29-tier quant ladder from 6.2 GB to 31.5 GB on top. "
            "Watch two Mac-specific things: a crash on an M2 Ultra with default settings, and a chat template "
            "that mis-renders tool calls until you substitute the Qwen3.6 one.",
            ["ggml-org/llama.cpp#27335", "ggml-org/llama.cpp#27139", "ggml-org/llama.cpp#27428"]),
        "ollama": cell("works", "Runs", 18.0, ("qwen3.8:27b", None),
            "In the library with 18/30/32/56 GB tags. Since Ollama now defaults to MLX on Apple Silicon, "
            "whether you get the MTP speedup depends on which path your tag resolves to - benchmark it rather "
            "than assuming.", []),
        "lmstudio": cell("works", "Runs", 17.6,
            ("GGUF or MLX 4-bit", "lmstudio-community/Qwen3.8-27B-GGUF"),
            "Curated in both formats, which makes it the cheapest way to settle the question this model raises: "
            "the MLX build decodes faster per token in principle, the GGUF build gets working MTP. Run both.",
            []),
        "omlx": cell("degraded", "Runs, degraded", 20.7,
            ("mlx-community/Qwen3.8-27B-OptiQ-4bit, 6 shards", "mlx-community/Qwen3.8-27B-OptiQ-4bit"),
            "oMLX ships native Metal kernels for the Qwen3.5 family, which is the right answer to this hybrid "
            "GDN architecture, and it is the strongest MLX option for the model. It is still degraded rather "
            "than clean: single-stream decode has regressed from about 36.5 to 24 tok/s on an M3 Ultra with the "
            "MTP path implicated, continuous batching on this architecture is unmeasured, and loading a second "
            "Qwen-family model can contaminate a resident engine.",
            ["jundot/omlx#2747", "jundot/omlx#2854", "jundot/omlx#2972", "jundot/omlx#3117",
             "jundot/omlx#2691"]),
        "vllmmlx": cell("degraded", "Runs, degraded", 20.7,
            ("mlx-community/Qwen3.8-27B-OptiQ-4bit, 6 shards", "mlx-community/Qwen3.8-27B-OptiQ-4bit"),
            "What holds this model back here is the runtime, not the model. Prefix caching is off on hybrid "
            "linear-attention architectures and speculative decoding is capped at k=1, so you pay full "
            "re-prefill on every turn and get none of the MTP head the checkpoint carries. The published "
            "Terminal-Bench 2.1 of 73.0 is the best agentic number among things that run - it is just not what "
            "you measure on this engine.",
            ["waybarrios/vllm-mlx#730", "waybarrios/vllm-mlx#731", "waybarrios/vllm-mlx#710",
             "ml-explore/mlx-lm#1446", "waybarrios/vllm-mlx#678", "waybarrios/vllm-mlx#641",
             "waybarrios/vllm-mlx#711", "waybarrios/vllm-mlx#729", "waybarrios/vllm-mlx#689",
             "waybarrios/vllm-mlx#658", "waybarrios/vllm-mlx#699"]),
        "mlxlm": cell("works", "Runs", 20.7,
            ("mlx-community/Qwen3.8-27B-OptiQ-4bit, 6 shards", "mlx-community/Qwen3.8-27B-OptiQ-4bit"),
            "The qwen3_5 class works for single-stream generation. The cache limitations that make this "
            "architecture painful on the servers above start here: ArraysCache is not trimmable, which is the "
            "cause of the k=1 speculative-decoding cap downstream.",
            ["ml-explore/mlx-lm#1446", "ml-explore/mlx-lm#1335"]),
        "vllmmetal": cell("works", "Runs", None, None,
            "The strongest MLX-backed option for this model, and worth being precise about why, because the "
            "name suggests otherwise: this is vLLM's scheduler and API over MLX as the compute layer. It "
            "pins `mlx==0.32.0` exactly, depends on mlx-lm and mlx-vlm, and its paged attention kernel is "
            "implemented as an `mlx::core::Primitive` subclass rather than running beside MLX. What it adds "
            "on top is hardware-specific: as of August 2026 it uses the M5 Neural Accelerator tensor units "
            "for MHA, GQA and MQA prefill, which no other engine here claims. `mlx-community/Qwen3.8-27B-8bit` is the project's own example "
            "checkpoint for the hybrid SDPA + GDN path, so this is the configuration they test. Prefix "
            "caching works but is opt-in on hybrid GDN - pass `--enable-prefix-caching` - which is a far "
            "better position than vllm-mlx, where it is off entirely. The open catch is that the built-in "
            "MTP head and prefix caching do not yet work together.",
            ['vllm-project/vllm-metal#610', 'vllm-project/vllm-metal#482', 'vllm-project/vllm-metal#646']),
        "ds4": cell("none", "Out of scope", None, None, "Not one of the three checkpoints ds4 loads.", []),
    },

    # ============================================================= MiniMax M3
    "m3": {
        "llamacpp": cell("works", "Runs", 194.9,
            ("MiniMax-M3-UD-Q3_K_XL, 5 shards", "unsloth/MiniMax-M3-GGUF"),
            "`minimax-m3` is in mainline llama.cpp, which flips this model from unreachable to practical. A "
            "22-tier ladder means you can choose your fit: UD-IQ3_XXS at 159.4 GB, UD-Q3_K_XL at 194.9 GB, "
            "UD-IQ4_XS at 207.6 GB, with the Q4 tiers (248-265 GB) needing more than one 256 GB machine. "
            "SWE-bench Verified 80.5% is the highest coding score on this page that fits a single box.",
            []),
        "ollama": cell("works", "Runs", 194.9, ("minimax-m3", None),
            "In the library. Check which quant the tag resolves to before pulling 250 GB onto a 256 GB machine.",
            []),
        "lmstudio": cell("works", "Runs", 194.9,
            ("bartowski or unsloth GGUF", "bartowski/MiniMax-M3-GGUF"),
            "GGUF path only in practice - the MLX conversion is an mlx-vlm build with open loader problems. "
            "LM Studio's llama.cpp engine is where this model works.", []),
        "omlx": cell("degraded", "Runs, degraded", 215.0,
            ("mlx-community/MiniMax-M3-4bit, converted with mlx-vlm 0.6.3", "mlx-community/MiniMax-M3-4bit"),
            "oMLX explicitly ships native kernels for MiniMax M3, so it is the MLX engine that intends to run "
            "this. In practice the checkpoint is `minimax_m3_vl` and loading has failed with 2225 vision-tower "
            "parameters rejected rather than skipped, alongside a model-type mapping error and an open question "
            "about which quant tiers the long-prefill fixes actually cover. Promising, not yet dependable.",
            ["jundot/omlx#1968", "jundot/omlx#1862", "jundot/omlx#2590"]),
        "vllmmlx": cell("blocked", "Blocked", 215.0,
            ("no mlx-lm text path; support unmerged", None),
            "There is no MiniMax M3 text backbone in mlx-lm - PR #1401 is still open - so there is nothing for "
            "vllm-mlx to wrap.",
            ["ml-explore/mlx-lm#1401"]),
        "mlxlm": cell("blocked", "Blocked", 215.0,
            ("mlx-vlm conversion only; text backbone PR open", None),
            "`minimax.py` covers the earlier MiniMax generation, not M3. The M3 text backbone is PR #1401, "
            "unmerged. The mlx-community 4-bit was produced with mlx-vlm, which is a different package and a "
            "different code path.",
            ["ml-explore/mlx-lm#1401"]),
        "vllmmetal": cell("blocked", "Blocked", None, None,
            "Not in the support matrix, and MiniMax M3's sparse attention would need its own kernel work.",
            []),
        "ds4": cell("none", "Out of scope", None, None, "Not one of the three checkpoints ds4 loads.", []),
    },

    # ====================================================== DeepSeek V4 Flash
    "v4flash": {
        "vllmmetal": cell("blocked", "Blocked", None, None,
            "Not in the support matrix. Latent attention generally is the weak spot here: the only MLA row "
            "carried is flagged as having no Metal kernel, and a specialised MLA paged-attention kernel is "
            "still at the RFC stage.",
            ['vllm-project/vllm-metal#360']),
        "ds4": cell("works", "Best path", 164.6,
            ("DeepSeek-V4-Flash Q4K experts, single file", "antirez/deepseek-v4-gguf"),
            "This is what ds4 exists for, and it is the strongest single answer on this page. Purpose-built C "
            "and Metal kernels for one architecture, with measured Metal numbers rather than estimates: 790 "
            "tok/s prefill and 39.4 tok/s generation at 2k context on a 128 GB M5 Max at q2, still 27.6 tok/s "
            "at 64k. Choose your fit - 86.7 GB at IQ2_XXS, 156 GB keeping DeepSeek's native MXFP4 experts, "
            "164.6 GB at Q4K. `ds4-server` speaks both OpenAI and Anthropic, persists KV to disk across "
            "restarts, and `--batched-session N` gives you real concurrent sessions. The open issues to read "
            "first are both agent-shaped: O(n squared) tokenization on large prompts, and stateless clients "
            "failing to extend the live KV session.",
            ["antirez/ds4#853", "antirez/ds4#816", "antirez/ds4#836", "antirez/ds4#805",
             "antirez/ds4#851", "antirez/ds4#839"]),
        "llamacpp": cell("degraded", "Runs, degraded", 151.3,
            ("unsloth or teamblobfish GGUF", "unsloth/DeepSeek-V4-Flash-0731-GGUF"),
            "`deepseek4` landed in mainline, so this works without a fork - but the open issues are unusually "
            "well aimed at agent use. The tokenizer overflows its stack on long tool output, tool calls with "
            "similar parameter names error out, there is a report of the model silently forgetting earlier "
            "context, and one of a 200-second prefill for a 10-token prompt. If you want this model, ds4 is the "
            "engine that was built for it.",
            ["ggml-org/llama.cpp#26965", "ggml-org/llama.cpp#25171", "ggml-org/llama.cpp#25796",
             "ggml-org/llama.cpp#25744"]),
        "ollama": cell("works", "Runs", 151.3, ("deepseek-v4-flash", None),
            "In the library as `deepseek-v4-flash`. The zero-effort route; the ceiling is lower than ds4's and "
            "you inherit whichever backend the tag resolves to.", []),
        "lmstudio": cell("works", "Runs", 151.3,
            ("GGUF via the llama.cpp engine", "nsparks/DeepSeek-V4-Flash-FP4-FP8-GGUF"),
            "Runs through the GGUF engine with the llama.cpp caveats above. Not through its MLX engine - there "
            "is no mlx-lm model class to use.", []),
        "omlx": cell("degraded", "Runs, degraded", 151.3,
            ("mlx-community/DeepSeek-V4-Flash-mxfp4, 33 shards", "mlx-community/DeepSeek-V4-Flash-mxfp4"),
            "oMLX does load DeepSeek V4 Flash, which no mlx-lm-derived engine can - so it has its own path. "
            "Speed is the problem: 4-17 tok/s on a 128 GB M5 Max, traced to the bundled MLX keeping a single "
            "residency set so weights fault instead of staying wired. On top of that, MXFP4 crashes on float32 "
            "activations, the prefix cache drops out with a signature mismatch, and thinking leaks into content "
            "on truncated turns. ds4 gets roughly ten times the decode rate on comparable hardware.",
            ["jundot/omlx#3121", "jundot/omlx#2469", "jundot/omlx#2493", "jundot/omlx#2606"]),
        "vllmmlx": cell("blocked", "Blocked", 151.3,
            ("mlx-community/DeepSeek-V4-Flash-mxfp4, 33 shards", "mlx-community/DeepSeek-V4-Flash-mxfp4"),
            "The quant exists and the footprint is ideal - 13B active reads about 7.5 GB per token, so "
            "bandwidth stops being the constraint - but the architecture is rejected outright. There is nothing "
            "to wrap: mlx-lm has no deepseek_v4 model class.",
            ["waybarrios/vllm-mlx#668", "ml-explore/mlx-lm#1233", "ml-explore/mlx-lm#1332"]),
        "mlxlm": cell("blocked", "Blocked", 151.3,
            ("quants published, but no deepseek_v4 model class", "mlx-community/DeepSeek-V4-Flash-4bit"),
            "The single most consequential gap in MLX. Several quants exist and their cards tell you to `pip "
            "install mlx-lm`, but there is no `deepseek_v4.py` in mlx-lm - support is PR #1233, still open. The "
            "residency-growth issue that aborts decode after about 11k tokens is filed against that PR's head, "
            "not against a released version. If you want an MLX-shaped route anyway, "
            "[ssd-moe/deepseek-v4-flash-mlx](https://github.com/ssd-moe/deepseek-v4-flash-mlx) is a custom MLX "
            "offload engine that streams experts from SSD to run this on a 48 GB Mac at about 4.5-5 tok/s - a "
            "different tradeoff from ds4's own SSD streaming, and far slower than either resident path.",
            ["ml-explore/mlx-lm#1233", "ml-explore/mlx-lm#1332", "ml-explore/mlx-lm#1192",
             "ml-explore/mlx-lm#1281", "ml-explore/mlx-lm#1443", "ml-explore/mlx-lm#1662",
             "ml-explore/mlx-lm#1404"]),
    },

    # =============================================================== GLM-5.2
    "glm52": {
        "vllmmetal": cell("blocked", "Blocked", None, None,
            "Not in the matrix. GLM-5.2's DSA attention is a latent-attention variant, and the MLA Metal "
            "kernel it would need is an open RFC.",
            ['vllm-project/vllm-metal#360']),
        "ds4": cell("works", "Best path", 211.1,
            ("GLM-5.2-UD-IQ2_XXS routed, single file", "antirez/glm-5.2-gguf"),
            "The highest agentic score reachable on Apple hardware, and ds4 is how you reach it. The routed "
            "IQ2_XXS build is 211.1 GB in one file, Q2_K is 262 GB, Q4_K is 434.2 GB. The interesting mode is "
            "tensor parallelism over Thunderbolt: two Macs hold half the routed experts each and work on the "
            "same token together, which cuts latency rather than just fitting a bigger model - demonstrated on "
            "a pair of 128 GB MacBooks. It needs an IQ2_XXS or Q2_K routed layout, so a routed Q4 GLM is "
            "rejected for that mode, and RDMA needs an IPv4 address on the cabled interface itself rather than "
            "the bridge.",
            ["antirez/ds4#845", "antirez/ds4#853", "antirez/ds4#816", "antirez/ds4#836",
             "antirez/ds4#805", "antirez/ds4#839"]),
        "omlx": cell("degraded", "Runs, degraded", 395.1,
            ("mlx-community/GLM-5.2-mxfp4, 76 shards", "mlx-community/GLM-5.2-mxfp4"),
            "oMLX ships fused DSA prefill kernels for GLM-5.2, and with them the difference is not marginal: "
            "845 tok/s versus about 29 on an M3 Ultra. The trap is that a plain `pip install` does not build "
            "them and the fallback is silent, so most people measuring this model on oMLX are measuring the "
            "wrong thing. Use the DMG or build with full Xcode. Open on top of that: repetition loops, mxfp4 "
            "failing to load on 0.4.4, and prefill throttling near the memory ceiling.",
            ["jundot/omlx#3006", "jundot/omlx#2099", "jundot/omlx#1927", "jundot/omlx#2208",
             "jundot/omlx#2137"]),
        "llamacpp": cell("works", "Runs", 216.7,
            ("GLM-5.2-UD-IQ1_S, 6 shards", "unsloth/GLM-5.2-GGUF"),
            "`glm-dsa` is in mainline. The quant ladder is the whole story: IQ1_S 216.7 GB, IQ2_XXS 238.5 GB, "
            "Q2_K_XL 253.9 GB, and Q4 tiers from 436 GB up - so a single 256 GB machine reaches only the "
            "1-2 bit tiers, and quality at IQ1 is a real question rather than a footnote. One structural "
            "annoyance: DSA has no V cache, but the K and V cache types are validated as a pair, so you cannot "
            "quantise K independently on the model with the least memory to spare.",
            ["ggml-org/llama.cpp#26382"]),
        "ollama": cell("works", "Runs", 253.9, ("glm-5.2", None),
            "In the library. On a single 256 GB machine you will need to be deliberate about the tag - the "
            "Q2-class build is already at 254 GB before any KV.", []),
        "lmstudio": cell("works", "Runs", 216.7,
            ("GGUF via the llama.cpp engine", "unsloth/GLM-5.2-GGUF"),
            "GGUF engine only in practice. The MLX build exists but mlx-lm cannot load it, and LM Studio's MLX "
            "engine is downstream of that.", []),
        "vllmmlx": cell("blocked", "Blocked", 395.1,
            ("mlx-community/GLM-5.2-mxfp4, 76 shards", "mlx-community/GLM-5.2-mxfp4"),
            "Blocked three ways through mlx-lm: the IndexShare indexers fail to load, DSA top-k evicts "
            "attention sinks, and at a measured 395.1 GB it sits squarely inside the >300 GB band where a "
            "one-shot mx.eval trips the GPU watchdog at load.",
            ["ml-explore/mlx-lm#1418", "ml-explore/mlx-lm#1443", "ml-explore/mlx-lm#1572"]),
        "mlxlm": cell("blocked", "Blocked", 395.1,
            ("mlx-community/GLM-5.2-mxfp4, 76 shards", "mlx-community/GLM-5.2-mxfp4"),
            "`glm_moe_dsa.py` exists, but the model does not load: IndexShare indexers, sink eviction under DSA "
            "top-k, and the >300 GB load watchdog.",
            ["ml-explore/mlx-lm#1418", "ml-explore/mlx-lm#1443", "ml-explore/mlx-lm#1572"]),
    },

    # ======================================================== DeepSeek V4 Pro
    "v4pro": {
        "vllmmetal": cell("blocked", "Blocked", None, None,
            "Same as Flash - the architecture is not in the matrix, and MLA has no Metal kernel yet.",
            ['vllm-project/vllm-metal#360']),
        "ds4": cell("works", "Best path", 464.6,
            ("PRO IQ2_XXS routed, single file; or the Q4 two-machine split", "antirez/deepseek-v4-gguf"),
            "ds4 runs PRO, with the honest caveat that it takes real hardware. The IQ2_XXS routed build is "
            "464.6 GB in one file - a 512 GB machine, or pooled across two 256 GB machines by pipeline "
            "parallelism. The Q4 split ships as two files of 457.5 GB and 442.0 GB, designed for a pair of "
            "512 GB Mac Studios with the coordinator taking layers 0-30 and the worker taking 31 to output. "
            "Measured: 9.56 tok/s generation on PRO q2 at 32k context on a 512 GB M3 Ultra. Note the 0813 "
            "refresh is not yet a supported checkpoint.",
            ["antirez/ds4#807", "antirez/ds4#845", "antirez/ds4#853", "antirez/ds4#816",
             "antirez/ds4#805"]),
        "llamacpp": cell("works", "Runs", 464.6,
            ("DeepSeek-V4-Pro-0813 GGUF", "unsloth/DeepSeek-V4-Pro-0813-GGUF"),
            "Same `deepseek4` path as Flash, so it loads - and inherits the same agent-shaped defects, on a "
            "model large enough that you will not be iterating quickly while you hit them.",
            ["ggml-org/llama.cpp#26965", "ggml-org/llama.cpp#25171", "ggml-org/llama.cpp#25796"]),
        "ollama": cell("works", "Runs", 464.6, ("deepseek-v4-pro", None),
            "In the library. Fit is the constraint, not availability.", []),
        "lmstudio": cell("works", "Runs", 464.6,
            ("GGUF via the llama.cpp engine", "teamblobfish/DeepSeek-V4-Pro-GGUF"),
            "GGUF engine only - there is no MLX model class for this architecture.", []),
        "omlx": cell("blocked", "Blocked", 800.0,
            ("no MLX quant of PRO published", None),
            "oMLX's DeepSeek V4 path exists, but nobody has published a PRO conversion, and the residency and "
            "MXFP4 problems open against Flash would apply at four times the size.",
            ["jundot/omlx#3121", "jundot/omlx#2469"]),
        "vllmmlx": cell("blocked", "Blocked", 800.0,
            ("no MLX quant published", None),
            "Same wall as Flash: no deepseek_v4 in mlx-lm to wrap, and no PRO quant if there were.",
            ["waybarrios/vllm-mlx#668", "ml-explore/mlx-lm#1233"]),
        "mlxlm": cell("blocked", "Blocked", 800.0,
            ("no MLX quant published", None),
            "No model class, no published conversion.",
            ["ml-explore/mlx-lm#1233", "ml-explore/mlx-lm#1443"]),
    },

    # =============================================================== Kimi K3
    "kimik3": {
        "llamacpp": cell("works", "Runs", 466.4,
            ("Kimi-K3-UD-Q1_0, 11 shards", "unsloth/Kimi-K3-GGUF"),
            "`kimi-k3` is in mainline, which makes the best open-weight agentic model on this page reachable on "
            "Apple hardware at all. Reachable, not comfortable: the smallest build is UD-Q1_0 at 466.4 GB, "
            "TQ1_0 is 508.9 GB, and Q2_K_XL is 861 GB. At 1-bit the question is no longer whether it loads but "
            "whether it is still the model whose Terminal-Bench 2.1 is 88.3. Vision is on a branch; the text "
            "backbone is not.",
            ["ggml-org/llama.cpp#26365"]),
        "ollama": cell("works", "Runs", 466.4, ("kimi-k3", None),
            "In the library. The tag you can actually run is decided by your pooled memory, not by preference.",
            []),
        "lmstudio": cell("works", "Runs", 466.4,
            ("GGUF via the llama.cpp engine", "unsloth/Kimi-K3-GGUF"),
            "GGUF engine. mlx-lm has no kimi_k3 class, so its MLX engine is not an option.", []),
        "omlx": cell("degraded", "Community builds only", 350.0,
            ("Kimi-K3-REAP80-MLX-mxfp4-q8, expert-pruned to 350 GB",
             "pipenetwork/Kimi-K3-REAP80-MLX-mxfp4-q8"),
            "There is an MLX route, and it is a compromise rather than a port. Community REAP builds prune "
            "routed experts - keeping 179 of 896 per layer - to get from 1.56 TB down to 350 GB, and the "
            "publisher measures 5.54 tok/s on a 512 GB M3 Ultra while documenting the degradation candidly, "
            "including Chinese output looping in that build. Note that pruning buys memory, not speed: "
            "per-token traffic depends on top-k and non-expert precision, so a 350 GB and a 451 GB build decode "
            "at the same rate. mlx-lm has no kimi_k3 model class, so these repos ship their own modelling code.",
            []),
        "vllmmlx": cell("blocked", "Blocked", 1400.0,
            ("no first-party MLX conversion", None),
            "mlx-lm carries kimi_k25 and kimi_linear but nothing for K3, so there is no architecture to wrap.",
            []),
        "mlxlm": cell("blocked", "Blocked", 1400.0,
            ("no kimi_k3 model class", None),
            "kimi_k25 and kimi_linear exist; K3 does not. Community REAP repos supply their own modelling code "
            "via auto_map rather than relying on mlx-lm.",
            ["ml-explore/mlx-lm#1572"]),
        "vllmmetal": cell("blocked", "Blocked", None, None,
            "Not in the support matrix, and no unpruned MLX build of K3 exists to try.",
            []),
        "ds4": cell("none", "Out of scope", None, None, "Not one of the three checkpoints ds4 loads.", []),
    },

    # =========================================================== Qwen3.8-Max
    "qwenmax": {
        "llamacpp": cell("works", "Runs", None, None,
            "The weights are public at `Qwen/Qwen3.8-2.4T-A95B` and the architecture is `qwen3_5_moe`, which "
            "llama.cpp already implements as `qwen35moe` - the same family as Qwen3.8-27B. So this is purely a "
            "capacity problem, not a support one. The ladder is brutal: UD-IQ4_XS is 1.31 TB, UD-IQ2_XXS is "
            "656.6 GB, and the smallest unpruned build is UD-Q1_0 at 397.3 GB. Someone has also published "
            "REAP-pruned GGUFs sized deliberately for 256 GB and 512 GB Macs.",
            []),
        "ollama": cell("blocked", "Not in library", None, None,
            "The `qwen3.8` library entry carries only 27B tags. Nothing at this size is published, which is "
            "reasonable - a 397 GB minimum does not suit a one-command pull.", []),
        "lmstudio": cell("works", "Runs", None, None,
            "Through the llama.cpp engine on the GGUF ladder. Nothing curated under lmstudio-community at this "
            "size, so you are pointing it at a community repo.", []),
        "omlx": cell("degraded", "Pruned builds only", None, None,
            "mlx-lm's `qwen3_5_moe` class covers the architecture, so this loads - but every published MLX "
            "build except one is REAP expert-pruned, and the one that is not is 805.6 GB. At these sizes the "
            "load-time watchdog on >300 GB checkpoints is also in play.",
            ["ml-explore/mlx-lm#1572", "jundot/omlx#2307"]),
        "vllmmlx": cell("degraded", "Pruned builds only", None, None,
            "Same picture as oMLX: the class exists, the unpruned MLX build is 805.6 GB, and everything smaller "
            "has had experts deleted.",
            ["ml-explore/mlx-lm#1572"]),
        "mlxlm": cell("degraded", "Pruned builds only", None, None,
            "`qwen3_5_moe.py` handles it. The constraint is what has been published: pruned builds from 360.9 GB "
            "up, or 805.6 GB unpruned.",
            ["ml-explore/mlx-lm#1572", "ml-explore/mlx-lm#1446"]),
        "vllmmetal": cell("degraded", "Untested at this size", None, None,
            "The matrix row covering Qwen3.5/3.6/3.8 notes that the 3.6 generation adds MoE, so this "
            "architecture is plausibly in scope - but nobody has run a 2.45T checkpoint through it, and no "
            "MLX build of this model exists that is not expert-pruned. Treat it as untested rather than "
            "supported.",
            ['ml-explore/mlx-lm#1572']),
        "ds4": cell("none", "Out of scope", None, None,
            "Not one of the three checkpoints ds4 loads.", []),
    },

    # ======================================================= Qwen3-Coder-Next
    "qcnext": {
        "llamacpp": cell("works", "Runs", None, None,
            "`qwen3next` is in mainline, and unsloth publishes the deepest quant ladder of any model here - "
            "38 tiers from 18.9 GB to 159.5 GB - so this fits almost any Mac at a precision you choose rather "
            "than one you accept. 3B active means decode stays cheap even on a laptop. Watch one report of "
            "garbled output, though it is filed against an abliterated finetune rather than the base weights.",
            ["ggml-org/llama.cpp#27727"]),
        "ollama": cell("works", "Runs", None, None,
            "`ollama run qwen3-coder-next`. Given the 3B active parameters and 256k context, this is the "
            "closest thing on the page to a drop-in local coding agent.", []),
        "lmstudio": cell("works", "Runs", None, None,
            "Curated in both formats under lmstudio-community - GGUF plus MLX at 4, 6 and 8-bit - which makes "
            "it one of the better-served models in the catalogue.", []),
        "omlx": cell("degraded", "Runs, degraded", None, None,
            "oMLX's own README uses this model in its example model directory, so it is a supported path. Two "
            "things to know: mlx-lm's hybrid cache is reported silently broken for Qwen3-Next, which removes "
            "prefix reuse without telling you, and continuous-batching prefill has been reported collapsing at "
            "exactly two concurrent requests.",
            ["ml-explore/mlx-lm#1162", "jundot/omlx#1783", "jundot/omlx#2252"]),
        "vllmmlx": cell("degraded", "Runs, degraded", None, None,
            "Loads on mlx-lm's qwen3_next class. The hybrid-cache defect upstream is the thing to check first, "
            "because a silently broken prompt cache costs you the whole reason to run a server.",
            ["ml-explore/mlx-lm#1162"]),
        "mlxlm": cell("degraded", "Runs, degraded", None, None,
            "`qwen3_next.py` exists and generates. The hybrid cache silently failing is filed here and "
            "propagates to every MLX server that wraps it.",
            ["ml-explore/mlx-lm#1162", "ml-explore/mlx-lm#1335"]),
        "vllmmetal": cell("works", "Runs", None, None,
            "Qwen3-Next is a supported family with its own row in the matrix, on the same hybrid SDPA + GDN "
            "path as Qwen3.8. Prefix caching is opt-in for that shape. At 3B active this is a natural fit "
            "for vLLM's continuous batching.",
            ['vllm-project/vllm-metal#610', 'vllm-project/vllm-metal#646']),
        "ds4": cell("none", "Out of scope", None, None,
            "Not one of the three checkpoints ds4 loads.", []),
    },

    # ==================================================== Qwen3.8-Flash-Next
    "q38fnext": {
        "llamacpp": cell("blocked", "Blocked", None, None,
            "This is a preview of the Qwen4 architecture, not a Qwen3 variant: the config reports "
            "`qwen4_exp`, and llama.cpp's architecture table has `qwen3next` but nothing for qwen4. Support is "
            "an open feature request. One GGUF has been published - a single UD-IQ1_S tier at 72.5 GB - but "
            "mainline has no loader for it, so the file exists ahead of the runtime.",
            ["ggml-org/llama.cpp#27741"]),
        "ollama": cell("blocked", "Blocked", None, None,
            "Not in the library, and it inherits the same missing architecture underneath.", []),
        "lmstudio": cell("blocked", "Blocked", None, None,
            "Nothing curated in either format. Both of its engines are downstream of the two projects that do "
            "not implement this architecture yet.", []),
        "omlx": cell("blocked", "Blocked", None, None,
            "No MLX conversion exists and mlx-lm has no qwen4 model class, so there is nothing to load. oMLX "
            "does ship native Qwen3.5 kernels, which is a reasonable signal that it would pick this up once "
            "upstream does.", []),
        "vllmmlx": cell("blocked", "Blocked", None, None,
            "Wraps mlx-lm, which has no qwen4 class. Nothing to wrap.", []),
        "mlxlm": cell("blocked", "Blocked", None, None,
            "The models directory carries qwen3_next but nothing for qwen4. This is the upstream gap every MLX "
            "engine on this page inherits.", []),
        "vllmmetal": cell("blocked", "Blocked", None, None,
            "The matrix covers Qwen3.5 through 3.8, not the qwen4_exp preview architecture. Same upstream "
            "gap every MLX engine here has.",
            []),
        "ds4": cell("none", "Out of scope", None, None,
            "Not one of the three checkpoints ds4 loads.", []),
    },
}

# Which engine each model card opens on, and the engine named in the index row.
BEST = {
    "glm47":    "llamacpp",
    "glm47f":   "llamacpp",
    "glimmer":  "llamacpp",
    "nemolight": "ollama",
    "gptoss":   "llamacpp",
    "gemma4":   "llamacpp",
    "qwen38":   "llamacpp",
    "m3":       "llamacpp",
    "v4flash":  "ds4",
    "glm52":    "ds4",
    "v4pro":    "ds4",
    "kimik3":   "llamacpp",
    "qwenmax":  "llamacpp",
    "qcnext":   "llamacpp",
    "q38fnext": "llamacpp",
}

# Tab order per model: best engine first, then the rest in roster order,
# dropping cells marked "none".
def engine_order(mid):
    best = BEST[mid]
    rest = [e["id"] for e in ENGINES
            if e["id"] != best and MATRIX[mid].get(e["id"], {}).get("s") != "none"]
    return [best] + rest


def repo_label(key):
    repo = key.split("#")[0]
    return {
        "waybarrios/vllm-mlx": "vllm-mlx",
        "ml-explore/mlx-lm": "mlx-lm",
        "ggml-org/llama.cpp": "llama.cpp",
        "jundot/omlx": "oMLX",
        "antirez/ds4": "ds4",
        "ollama/ollama": "ollama",
        "lmstudio-ai/lmstudio-bug-tracker": "LM Studio",
    }.get(repo, repo)


# ---------------------------------------------------------------------------
# Ollama and LM Studio issue metadata, plus the cross-cutting lists.
# ---------------------------------------------------------------------------

EMETA.update({
    "ml-explore/mlx-lm#1162": ("high", "Qwen3-Next hybrid cache silently fails, breaking the prompt cache",
        "Silent, and it removes prefix reuse - the single biggest win on multi-turn agent traffic. Every MLX "
        "server that wraps mlx-lm inherits it, so the model looks fine while every turn re-prefills."),
    "jundot/omlx#1783": ("high", "Continuous batching prefill collapses at exactly two concurrent requests",
        "Recovers at higher concurrency, which makes it easy to miss in a benchmark that jumps straight to "
        "eight. Two concurrent requests is the most common real case."),
    "jundot/omlx#2252": ("medium", "A broken-load DFlash helper poisons concurrent requests to an unrelated model",
        "Cross-contamination between models in the same server, on the Qwen3-Next batched path specifically."),
    # ---------------- Ollama ----------------
    "ollama/ollama#15813": ("critical", "Metal backend crash on Apple M5: bfloat/half type mismatch",
        "An M5-specific crash in the Metal matmul path. If you are buying an M5 machine, this is the one to "
        "check is closed before you plan around Ollama on it."),
    "ollama/ollama#17656": ("high", "muse-glimmer:30b-mlx is built from nvfp4-dflash layers, not real MLX weights",
        "The tag says MLX and the manifest says something else, so you may not be running what you think you "
        "are. Worth knowing generally: an Ollama tag is a manifest, not a guarantee about the underlying build."),
    "ollama/ollama#17776": ("high", "Qwen3.8-27B MTP variants are 2x slower than non-MTP on Apple Silicon",
        "Speculative decoding making decode twice as slow is the opposite of the intent. On this model MTP is "
        "the main reason to prefer one engine over another, so a negative result here matters."),
    "ollama/ollama#17638": ("high", "gpt-oss: HTTP 500 'error parsing tool call' on a call its own model generated",
        "The server rejects output produced by the model it shipped. From the agent's side it is a hard failure "
        "on a turn that was otherwise correct."),
    "ollama/ollama#17323": ("high", "Bare-JSON tool-call models silently drop content generated after the call",
        "The call survives and the accompanying text does not. Silent truncation is worse than an error because "
        "the agent proceeds on a partial turn."),
    "ollama/ollama#17878": ("medium", "Embeddings silently return all-zero vectors under sustained load",
        "HTTP 200, plausible usage numbers, and useless vectors. Not an LLM path, but it says something about "
        "how failures surface here."),
    "ollama/ollama#14116": ("medium", "Tiered context length can exhaust VRAM",
        "The automatic context sizing can commit more memory than the machine has. On a Mac that is unified "
        "memory, so it is the whole machine rather than just the model."),
    "ollama/ollama#17783": ("medium", "gemma4:31b-mlx grows in memory over a session",
        "Resident size climbing during use, on the MLX path. Matters most on a machine sized close to the model."),
    "ollama/ollama#17569": ("medium", "x/mlxrunner panics importing a plain Qwen3 MLX 4-bit model",
        "An index-out-of-range in the MLX runner's dense MLP forward. Importing an ordinary mlx-community "
        "checkpoint is a normal thing to want to do."),

    # ---------------- LM Studio ----------------
    "lmstudio-ai/lmstudio-bug-tracker#2323": ("critical", "MLX engine silently clamps context to 4864 tokens, ignoring all overrides",
        "Filed against a hybrid linear-attention model - the Qwen3.8 shape. A silent 4864-token ceiling makes "
        "any agent workload fail in a way that looks like the model being stupid rather than the engine being "
        "misconfigured."),
    "lmstudio-ai/lmstudio-bug-tracker#2273": ("high", "MLX quants shown as having no tool use when they do",
        "The capability badge is wrong, so the app steers you away from working tool-calling builds. Cosmetic "
        "in code, decision-changing in practice."),
    "lmstudio-ai/lmstudio-bug-tracker#2265": ("high", "MLX Gemma 4 silently ignores attached images and confabulates a description",
        "The GGUF build of the same model handles them. A vision model that invents what it cannot see is the "
        "worst available failure mode, and it is engine-specific."),
    "lmstudio-ai/lmstudio-bug-tracker#2240": ("medium", "Too much memory allocated",
        "Over-allocation relative to the model. On a 256 GB machine running a 200 GB model there is no slack to "
        "absorb it."),
    "lmstudio-ai/lmstudio-bug-tracker#2243": ("low", "Native MLX tool calling: parser coverage requests",
        "Tool-call parsing is per-family, so a model whose format has no parser returns its calls as text. Track "
        "this if your model is not in the supported list."),
    "lmstudio-ai/lmstudio-bug-tracker#2324": ("low", "Catalog entries show 'Invalid Key ID' with no download options",
        "A catalogue-side failure rather than an inference one, but the catalogue is how most people get models "
        "into this app."),
})

# Server-wide issues per engine: things that affect whichever model you pick.
CROSS_BY_ENGINE = {
    "llamacpp": ["ggml-org/llama.cpp#25967", "ggml-org/llama.cpp#27427",
                 "ggml-org/llama.cpp#26382", "ggml-org/llama.cpp#26894"],
    "ollama": ["ollama/ollama#15813", "ollama/ollama#17638", "ollama/ollama#17323",
               "ollama/ollama#14116", "ollama/ollama#17656", "ollama/ollama#17878"],
    "lmstudio": ["lmstudio-ai/lmstudio-bug-tracker#2323", "lmstudio-ai/lmstudio-bug-tracker#2273",
                 "lmstudio-ai/lmstudio-bug-tracker#2265", "lmstudio-ai/lmstudio-bug-tracker#2240",
                 "lmstudio-ai/lmstudio-bug-tracker#2243"],
    "omlx": ["jundot/omlx#2307", "jundot/omlx#2137"],
    "vllmmetal": ["vllm-project/vllm-metal#646", "vllm-project/vllm-metal#482",
                  "vllm-project/vllm-metal#450", "vllm-project/vllm-metal#360"],
    "vllmmlx": ["waybarrios/vllm-mlx#619", "waybarrios/vllm-mlx#584", "waybarrios/vllm-mlx#672",
                "waybarrios/vllm-mlx#546", "waybarrios/vllm-mlx#627", "waybarrios/vllm-mlx#682",
                "waybarrios/vllm-mlx#732", "waybarrios/vllm-mlx#570"],
    "mlxlm": ["ml-explore/mlx-lm#1662", "ml-explore/mlx-lm#1335", "ml-explore/mlx-lm#1572"],
    "ds4": ["antirez/ds4#853", "antirez/ds4#816", "antirez/ds4#836", "antirez/ds4#805",
            "antirez/ds4#845", "antirez/ds4#839", "antirez/ds4#860"],
}

# Release feeds. `scheme` picks how mlx-watch reads a version:
#   release - /releases/latest
#   semver  - first v-prefixed entry in /tags (llama.cpp also publishes hourly b##### builds)
#   none    - the project ships no tags; build from the default branch
RELEASE_FEEDS = [
    {"engine": "llamacpp", "repo": "ggml-org/llama.cpp", "scheme": "semver",
     "note": "also publishes hourly b##### builds"},
    {"engine": "ollama", "repo": "ollama/ollama", "scheme": "release", "note": ""},
    {"engine": "lmstudio", "repo": None, "scheme": "none",
     "note": "closed source; no public tag feed, see the in-app release notes"},
    {"engine": "omlx", "repo": "jundot/omlx", "scheme": "release", "note": ""},
    {"engine": "vllmmetal", "repo": "vllm-project/vllm-metal", "scheme": "release", "note": ""},
    {"engine": "vllmmlx", "repo": "waybarrios/vllm-mlx", "scheme": "release", "note": ""},
    {"engine": "mlxlm", "repo": "ml-explore/mlx-lm", "scheme": "release", "note": ""},
    {"engine": "ds4", "repo": "antirez/ds4", "scheme": "none",
     "note": "untagged by design (ds4#839); build from main"},
]


# ---------------------------------------------------------------------------
# Which quant family each engine loads, so one target build is chosen per model
# per cluster size rather than each engine being pinned to a different rung.
# ---------------------------------------------------------------------------

FAM = {"llamacpp": "gguf", "ollama": "gguf", "lmstudio": "gguf",
       "omlx": "mlx", "vllmmetal": "mlx", "vllmmlx": "mlx", "mlxlm": "mlx", "ds4": "ds4"}

# LM Studio ships both engines, so for a model whose MLX build is the better one
# it should be judged on that ladder instead.
FAM_OVERRIDE = {
    ("lmstudio", "glm47f"): "mlx",
    ("lmstudio", "qwen38"): "mlx",
    ("lmstudio", "gemma4"): "gguf",
}

# Fidelity bands, keyed on measured bits per weight rather than the quant's name.
# Thresholds follow the published evidence: Unsloth's Dynamic 3.0 notes state
# plainly that "1-bit should not be used for agentic use-cases" - tool calling
# breaks down, responses loop or come back empty - and put the practical floor at
# 2-bit. Their Qwen3.5 sweep shows 99.9% KL divergence rising from 0.41 at
# Q4_K_XL to 1.53 at IQ3_XXS, 2.91 at Q2_K_XL and 4.22 at IQ2_XXS, with a cliff
# in 32-token prediction accuracy from ~25% to under 10% below the 2-bit tier.
# Independent testing finds logical reasoning fairly quantisation-resistant while
# arithmetic starts degrading below 4 bits.
BANDS = [
    (4.0, "full", "Full fidelity",
     "At or above 4 bits per weight, which is where measured KL divergence stays low and "
     "arithmetic and tool calling hold up."),
    (3.0, "mild", "Reduced fidelity",
     "3 to 4 bits per weight. Reasoning survives this range well, but arithmetic and long "
     "tool-calling chains start to drift. Fine for drafting, worth verifying for agent work."),
    (2.0, "low", "Degraded",
     "2 to 3 bits per weight. Measured KL divergence here is roughly 7x the 4-bit tier. "
     "Expect weaker instruction adherence and less reliable tool calls; keep tool schemas small."),
    (0.0, "unusable", "Below agentic-usable",
     "Under 2 bits per weight. Unsloth's own guidance is that 1-bit builds "
     "should not be used for agentic use-cases: tool calling breaks down, generations loop "
     "without a high presence penalty, and responses can come back empty. It loads. That is "
     "the most that should be claimed for it."),
]

# Per model and family, what to say when the fitting rung is not full fidelity -
# or when a nominally low tier is better than its name suggests.
FIDELITY_NOTES = {
    ("v4flash", "ds4"):
        "ds4's 2-bit builds are the exception to the usual warning. Only the routed experts are "
        "quantised - up and gate at IQ2_XXS, down at Q2_K - while shared experts, projections and "
        "routing are left untouched, and the result is scored against a 100-case fixture of official "
        "DeepSeek continuations. The project states these behave well under coding agents and call "
        "tools reliably, which is a stronger claim than anyone makes for a generic 2-bit GGUF.",
    ("glm52", "ds4"):
        "Same asymmetric approach as the DeepSeek builds: routed expert gate/up and down tensors are "
        "quantised while dense and control tensors stay at Q8/F32. Two-Mac tensor parallelism needs an "
        "IQ2_XXS or Q2_K routed layout specifically - a routed Q4 build is rejected for that mode.",
    ("v4pro", "ds4"):
        "PRO's routed experts get the same asymmetric treatment. The Q4 pair is a layer split for two "
        "512 GB machines rather than a single-machine build.",
    ("gptoss", "gguf"):
        "MXFP4 at 4.23 bits is not a downgrade here - it is the precision OpenAI released. There is no "
        "higher-fidelity build to reach for, and a Q8 GGUF of it would only pad the same weights.",
    ("v4flash", "gguf"):
        "DeepSeek released these experts in MXFP4, so the ladder tops out near 4.5 bits rather than 8. "
        "The Q8 build is not eight-bit weights; it is the native 4-bit experts in a wider container.",
    ("v4pro", "gguf"):
        "Same as Flash: the released experts are already MXFP4, so ~4.4 bits is the ceiling, not a "
        "compromise.",
    ("gemma4", "gguf"):
        "Google publishes this as a quantisation-aware-trained build, so its 4-bit tier lost less than "
        "a post-hoc 4-bit of the same model would. Prefer the QAT repo over a community requantisation.",
    ("kimik3", "mlx"):
        "These are not quantised down - they are expert-pruned. REAP scores each expert and deletes the "
        "rest, keeping 179 of 896 per layer in the 350 GB build, so the surviving weights are near "
        "lossless mxfp4 while the model's capacity is cut by four fifths. A bits-per-weight figure would "
        "flatter it. The publisher documents the damage candidly, including Chinese output looping in the "
        "REAP-80 build, and code holding up better than language because code experts cluster densely.",
    ("kimik3", "gguf"):
        "Every Kimi K3 GGUF tier that fits any Mac cluster is under 2.5 bits per weight, and the ones "
        "that fit two 256 GB machines are 1.3 to 1.7 bits - squarely inside the band its own quantiser "
        "warns against for agentic use. The 88.3 Terminal-Bench figure was not measured on anything you "
        "can run here.",
    ("q38fnext", "gguf"):
        "The only published GGUF is a single UD-IQ1_S at 72.5 GB, which works out to 3.22 bits per weight "
        "against the full 180B checkpoint because the 51B n-gram embedding table dominates it. There is no "
        "ladder to choose from, and no mainline loader for the file either.",
    ("qwenmax", "gguf"):
        "Nothing on this ladder is comfortable. The smallest unpruned build is 1.30 bits per weight, and the "
        "first tier that clears 2 bits is 656.6 GB. The REAP-256GB and REAP-512GB builds are expert-pruned to "
        "hit those memory targets, which trades capacity for fit rather than precision.",
    ("qwenmax", "mlx"):
        "Only one published MLX build is not expert-pruned, and it is 805.6 GB. Everything that fits a "
        "realistic Mac cluster has had between half and three quarters of its experts deleted.",
    ("qcnext", "mlx"):
        "The MLX ladder stops at 4-bit (44.8 GB) - there is no 3-bit rung - while the GGUF ladder runs all the "
        "way down to 18.9 GB. On a 32 or 48 GB machine that difference decides whether the model fits at all.",
    ("glm47", "mlx"):
        "The MLX ladder has no 3-bit rung, so it steps straight from 4-bit at 198.6 GB down to "
        "expert-pruned REAP builds. The GGUF ladder is finer-grained in exactly the range that matters "
        "on a 256 GB machine.",
}


# ---------------------------------------------------------------------------
# Use cases: a curated ranking per job, not a computed one.
#
# The scores on this page come from different benchmarks with different scales,
# and the page already warns that Terminal-Bench 2.0 and 2.1 cannot be ranked
# against each other. So sorting models by "score" would invent a comparison
# that does not exist. Each list below is an explicit ordering with the evidence
# that justifies each place, and the browser walks it top-down and takes the
# first model that actually fits the selected cluster at a usable precision.
#
# `gate` is the lowest fidelity band acceptable for that job. Agentic and
# terminal work gate at "low" (2 bits) because tool calling is the first thing
# to break under heavy quantisation; bulk generation tolerates more.
# ---------------------------------------------------------------------------

USE_CASES = [
    {"id": "agentic", "label": "Agentic & tool use", "gate": "mild",
     "axis": "Tool-use and agent benchmarks. Scores are from different suites - they justify each "
             "placement rather than being directly comparable.",
     "rank": [("kimik3", "MCPMark-Verified", "94.5"), ("qwenmax", "Terminal-Bench 2.1", "86.6"),
              ("glm52", "Terminal-Bench 2.1", "81.0"),
              ("q38fnext", "CoWorkBench", "73.9"), ("glm47", "τ²-Bench", "87.4"),
              ("gemma4", "τ²-Bench", "86.4"), ("qwen38", "Terminal-Bench 2.1", "73.0"),
              ("glimmer", "MCP Atlas", "75.5"), ("m3", "MCP Atlas", "74.2"),
              ("qcnext", "Terminal-Bench 2.0", "36.2"), ("glm47f", "τ²-Bench", "79.5"),
              ("gptoss", "τ-Bench Retail", "67.8"), ("v4pro", "GDPval-AA", "1554"),
              ("v4flash", "GDPval-AA max effort", "1388")]},
    {"id": "coding", "label": "Coding", "gate": "mild",
     "axis": "Ordered on SWE-bench Verified where published, since it is the one coding benchmark most "
             "of these models report.",
     "rank": [("v4pro", "SWE-bench Verified", "80.6%"), ("m3", "SWE-bench Verified", "80.5%"),
              ("qwenmax", "SWE-bench Pro", "67.7"),
              ("glimmer", "SWE-bench Verified", "76.0"), ("qcnext", "SWE-bench Verified", "74.2%"),
              ("glm47", "SWE-bench Verified", "73.8%"), ("gptoss", "SWE-bench Verified", "62.4%"),
              ("q38fnext", "SWE-bench Pro", "62.5"), ("glm52", "SWE-bench Pro", "62.1%"),
              ("qwen38", "SWE-bench Pro", "61.7"), ("glm47f", "SWE-bench Verified", "59.2%"),
              ("gemma4", "SWE-bench Verified", "52.0%"), ("nemolight", "SWE-bench Verified", "51.56"),
              ("kimik3", "LiveBench Coding", "81.45")]},
    {"id": "terminal", "label": "Terminal & CLI work", "gate": "mild",
     "axis": "Terminal-Bench 2.1 only, so these are directly comparable. GLM-4.7 is excluded because "
             "its 41.0 is on v2.0, a different benchmark.",
     "rank": [("kimik3", "Terminal-Bench 2.1", "88.3"), ("qwenmax", "Terminal-Bench 2.1", "86.6"),
              ("glm52", "Terminal-Bench 2.1", "81.0"),
              ("qwen38", "Terminal-Bench 2.1", "73.0"), ("m3", "Terminal-Bench 2.1", "66.0"),
              ("glimmer", "Terminal-Bench 2.1", "51.7")]},
    {"id": "computer", "label": "Computer use (GUI)", "gate": "mild",
     "axis": "OSWorld and AndroidWorld, which are different suites - AndroidWorld figures are comparable to each other, OSWorld ones are not comparable to OSWorld-Verified. Only a handful of these models report computer-use numbers at all.",
     "rank": [("kimik3", "OSWorld-Verified", "84.8"), ("q38fnext", "AndroidWorld", "84.5"),
              ("qwen38", "AndroidWorld", "81.9"), ("glimmer", "OSWorld-Verified", "65.9")]},
    {"id": "concurrency", "label": "Many parallel streams", "gate": "mild",
     "axis": "Ranked by active parameters and KV cost per token, because at concurrency those decide "
             "throughput far more than the benchmark scores do.",
     "rank": [("qcnext", "3B active, 24 KiB/token", "cheapest overall"),
              ("q38fnext", "6B active, 24 KiB/token", "cheap but blocked"),
              ("glm47f", "3B active, 53 KiB/token", "cheapest"), ("nemolight", "3B active, 6 KiB/token", "cheapest KV"),
              ("gptoss", "5.1B active, 36 KiB/token", "strong"), ("glimmer", "dense 30B, 13 KiB/token", "cheap KV"),
              ("qwen38", "dense 27.8B, 64 KiB/token", "good"), ("v4flash", "13B active, 48 KiB/token", "large but cheap"),
              ("m3", "23B active, 120 KiB/token", "expensive KV"), ("glm47", "32B active, 368 KiB/token", "KV-bound")]},
    {"id": "longctx", "label": "Long context", "gate": "mild",
     "axis": "Ranked by KV bytes per token against the advertised ceiling - the models with a 1M window "
             "and latent attention are the only ones where a long context is affordable.",
     "rank": [("kimik3", "1M ctx at 27 KiB/token", "29 GB full"), ("v4flash", "1M ctx at 48 KiB/token", "52 GB full"),
              ("v4pro", "1M ctx at 69 KiB/token", "74 GB full"), ("glm52", "1M ctx at 88 KiB/token", "94 GB full"),
              ("m3", "1M ctx at 120 KiB/token", "129 GB full"), ("qcnext", "262k ctx at 24 KiB/token", "6 GB full"),
              ("q38fnext", "262k ctx at 24 KiB/token", "6 GB full"),
              ("qwen38", "262k ctx at 64 KiB/token", "17 GB full"),
              ("glm47f", "203k ctx at 53 KiB/token", "11 GB full"),
              ("gemma4", "262k ctx at 160 KiB/token", "43 GB full")]},
]
