# Apple LLM Performance Tracker

Which open-weight models actually run well on which Apple silicon, and through
which engine.

**Live site: https://dreamingwell.github.io/apple-llm-performance/**

Pick a CPU model, a memory size and a machine count. The page then tells you,
per model: whether it runs, which engine to use, which quantisation that engine
should load at that memory size, how much fidelity you give up, and how many
concurrent contexts fit in what's left.

Corrections and additions are welcome — open an issue or send a PR. Everything
the page renders from is in this repo, in plain Python data structures.

## This was made by AI, and AI contributions are welcome

The research, the data and the code here were produced by Claude working from
published model cards, engine source trees and issue trackers, with a human
directing it and pushing back. We are saying so up front because you should
weigh the page accordingly: it is a well-sourced secondary compilation, not
first-hand measurement, and every figure links to where it came from.

Because of that, **we welcome reasonable AI-assisted contributions.** Use
whatever tools you like. What we ask is the same thing we ask of ourselves:

- Cite the source for every number — a repo, a model card, an issue, a commit.
- Don't invent a benchmark score, a file size or an issue number. If it can't be
  linked, leave it out and say it's unverified.
- Check that a quant actually loads on the engine you're claiming, rather than
  inferring support from a file existing.
- Keep it to a reviewable size. A PR touching one model is easy to check; a
  sweeping rewrite is not.

**We are especially interested in new and useful models.** If something has
shipped open weights and runs on Apple silicon, we want it here — see
[CONTRIBUTING.md](CONTRIBUTING.md), or [AGENTS.md](AGENTS.md) if you are an agent.

## Engines covered

| Engine | Format | Interface | API |
|---|---|---|---|
| [llama.cpp](https://github.com/ggml-org/llama.cpp) | GGUF | CLI + `llama-server` | OpenAI + Anthropic |
| [Ollama](https://github.com/ollama/ollama) | MLX on Apple silicon, GGUF elsewhere | background server + CLI | OpenAI + native |
| [LM Studio](https://lmstudio.ai) | GGUF and MLX | desktop app + `lms` + server | OpenAI |
| [oMLX](https://github.com/jundot/omlx) | MLX | menu-bar app + server | OpenAI + Anthropic |
| [vLLM Metal](https://github.com/vllm-project/vllm-metal) | MLX | CLI + the vLLM server | OpenAI |
| [vllm-mlx](https://github.com/waybarrios/vllm-mlx) | MLX | server | OpenAI + Anthropic |
| [mlx-lm](https://github.com/ml-explore/mlx-lm) | MLX | CLI + `mlx_lm.server` | OpenAI (minimal) |
| [DwarfStar / ds4](https://github.com/antirez/ds4) | purpose-built GGUF | CLI + server + agent | OpenAI + Anthropic |

### Generative media

None of the servers above can load a diffusion or audio model, so these are a
separate set. The page pairs models with engines of the same modality and never
shows one against the other.

| Engine | Output | Interface |
|---|---|---|
| [mflux](https://github.com/filipstrand/mflux) | image | CLI + Python |
| [MLX-Audio](https://github.com/Blaizzy/mlx-audio) | audio - TTS, STT, music | CLI + Python + web UI |
| [MLX-Video](https://github.com/Blaizzy/mlx-video) | video, image | CLI + Python |
| [DiffusionKit](https://github.com/argmaxinc/DiffusionKit) | image | CLI + Python |

Every one of them speaks HTTP. None is desktop-only.

## Building it

Standard library only. No install step, no dependencies.

```sh
python3 tracker/validate.py   # checks every record in data/
python3 tracker/build.py      # writes docs/index.html
```

Both run in CI on every push and pull request, so a contribution's shape is
machine-checked before anyone reads it.

`docs/` is generated and deliberately **not** committed — Pages serves the
artifact that `.github/workflows/deploy.yml` builds on every push to `main`, so
a merged PR is a deployment and nobody has to resolve conflicts in a 780 KB
generated HTML file.

To refresh the tracked issue states (needs a token — the API allows 60
unauthenticated requests an hour and this makes ~117):

```sh
GITHUB_TOKEN=$(gh auth token) python3 tracker/probe.py > tracker/watch-state.txt
```

`.github/workflows/refresh.yml` does that twice a day and commits the result,
which triggers a deploy. `tracker/watch.sh` is the same loop for running locally.

To re-measure one model's quant ladder from Hugging Face (this one hits the
network):

```sh
python3 tracker/measure.py --model qwen38
```

It rewrites the `LADDER` block in that model's file and nothing else.

## What's where

One record, one file. A model, an engine, a use case and an issue tracker each
own exactly one file, so two people adding two models never touch the same file.

```
data/models/<id>.py       one model: identity, scores, per-engine status,
                          measured quant ladder, KV geometry
data/engines/<id>.py      one engine: what it is, its API, its cross-cutting issues
data/use_cases/<id>.py    one "What for?" category and its curated ranking
data/issues/<repo>.py     tracked issues for one upstream repository
data/pr_keys.py           which issue keys are pull requests
data/machines.py          every M-series chip: bandwidth, memory options,
                          Thunderbolt generation

tracker/registry.py       loads data/ and assembles it; the only file that
                          knows the schema
tracker/validate.py       enforces the schema — CI runs this
tracker/render_status.py  the HTML template and the page's prose
tracker/bands.py          fidelity thresholds and per-model quant caveats
tracker/throughput.py     the decode ceiling, and what it assumes
tracker/build.py          renders docs/index.html
tracker/measure.py        re-measures a quant ladder from the Hugging Face API
tracker/probe.py          refreshes watch-state.txt from the GitHub API
tracker/watch-state.txt   last polled state of every tracked issue
tools/check_output.py     sanity-checks the rendered page — CI runs this
notes/                    design notes; start with tokens-per-second.md
assets/                   social card source and output
docs/                     GENERATED, gitignored — the built site
```

Start in `data/models/` — that's where the facts are. Everything in `tracker/`
is plumbing around them.

If you are an AI agent working on this repository, read
[AGENTS.md](AGENTS.md) first. It is the maintenance contract: where to look for
new models, how to derive each figure, and the pitfalls that have already
bitten us here.

## How the numbers are derived

- **Weights** are summed file sizes from the linked Hugging Face repository —
  safetensors for MLX builds, GGUF for the rest. Measured, not estimated.
- **Bits per weight** is `bytes * 8 / total parameters`, so it is the effective
  figure rather than whatever the quant is named. Those diverge badly on MoE
  models: GLM-5.2's `UD-IQ1_S` is really 2.33 bpw, because the non-expert
  tensors are carried at higher precision.
- **Expert-pruned builds** (REAP and similar) carry no bits-per-weight number at
  all. Their loss is structural — whole experts deleted — and a bits figure
  would flatter them.
- **Fidelity bands** follow published evidence rather than opinion. Unsloth's
  Dynamic 3.0 notes state plainly that 1-bit builds should not be used for
  agentic work; their Qwen3.5 sweep puts 99.9% KL divergence at 0.41 for
  Q4_K_XL, 1.53 at IQ3_XXS, 2.91 at Q2_K_XL and 4.22 at IQ2_XXS.
- **KV cost per token** is derived from each model's published `config.json`,
  counting only layers whose cache grows with context. Sliding-window layers are
  bounded by the window and linear/Mamba/KDA layers hold a fixed recurrent
  state, so neither belongs in a per-token figure. Latent-attention models store
  one compressed vector per layer instead of separate K and V, which is why they
  are so much cheaper.
- **Use-case rankings are curated, not computed.** The benchmarks are not
  mutually comparable — Terminal-Bench 2.0 and 2.1 are different tests — so
  sorting by "score" would invent a comparison that does not exist. Each list is
  explicit, with the evidence for each placement, and the browser picks the
  highest-ranked model that actually fits at a usable precision.
- **Fit** assumes a 90% wired-memory limit plus framework overhead — ~10 GB for
  an LLM server holding a paged KV pool, ~1.5 GB for an image or audio runtime.
  It answers "does this load", not "does this run well".
- **Tokens per second comes in two classes and they are never mixed.** A
  *measurement* is somebody else's run, shown with the machine, build and context
  it came off and a link to whoever took it. A *ceiling* is `bandwidth ÷ bytes
  read per token`, marked `≤`, and it is an upper bound rather than a prediction
  — decoding at batch 1 reads the active weights plus the attended KV for every
  token and reuses almost none of it, so memory bandwidth caps it. Nothing is
  self-reported to us: a tokens-per-second figure with no build and no context
  compares to nothing. The reasoning, the failure modes and the bound checked
  against every complete measurement on the page are in
  [notes/tokens-per-second.md](notes/tokens-per-second.md) and in the page's own
  "Tokens per second" panel.

## Limits worth stating plainly

Nothing here has been benchmarked on this hardware by us. Benchmark scores are
vendor- or aggregator-reported. Issue states are a twice-daily snapshot. Every
memory figure, and every throughput figure marked `≤`, is arithmetic over
published specifications rather than a measurement — the handful of real
throughput measurements on the page are other people's, and say whose. Treat the page as a shortlist filter and verify anything you intend
to spend money on.

If you have measured something on real hardware, that is the most valuable kind
of contribution — see [CONTRIBUTING.md](CONTRIBUTING.md).

## Licence

MIT for the code. The benchmark figures and issue references belong to their
respective projects and are cited on the page.
