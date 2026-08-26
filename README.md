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
[CONTRIBUTING.md](CONTRIBUTING.md) for the five files to touch.

## Engines covered

| Engine | Format | Interface | API |
|---|---|---|---|
| [llama.cpp](https://github.com/ggml-org/llama.cpp) | GGUF | CLI + `llama-server` | OpenAI + Anthropic |
| [Ollama](https://github.com/ollama/ollama) | MLX on Apple silicon, GGUF elsewhere | background server + CLI | OpenAI + native |
| [LM Studio](https://lmstudio.ai) | GGUF and MLX | desktop app + `lms` + server | OpenAI |
| [oMLX](https://github.com/jundot/omlx) | MLX | menu-bar app + server | OpenAI + Anthropic |
| [vllm-mlx](https://github.com/waybarrios/vllm-mlx) | MLX | server | OpenAI + Anthropic |
| [mlx-lm](https://github.com/ml-explore/mlx-lm) | MLX | CLI + `mlx_lm.server` | OpenAI (minimal) |
| [DwarfStar / ds4](https://github.com/antirez/ds4) | purpose-built GGUF | CLI + server + agent | OpenAI + Anthropic |

Every one of them speaks HTTP. None is desktop-only.

## Building it

Standard library only. No install step, no network access.

```sh
python3 tracker/build.py      # writes docs/index.html
```

`docs/` is generated and deliberately **not** committed — Pages serves the
artifact that `.github/workflows/deploy.yml` builds on every push to `main`, so
a merged PR is a deployment and nobody has to resolve conflicts in a 620 KB
generated HTML file.

To refresh the tracked issue states (needs a token — the API allows 60
unauthenticated requests an hour and this makes ~116):

```sh
GITHUB_TOKEN=$(gh auth token) python3 tracker/probe.py > tracker/watch-state.txt
```

`.github/workflows/refresh.yml` does that twice a day and commits the result,
which triggers a deploy. `tracker/watch.sh` is the same loop for running locally.

To re-measure the quant ladders from Hugging Face (this one does hit the
network, and takes a couple of minutes):

```sh
python3 tracker/build_quants.py     # regenerates tracker/quants.py
```

## What's where

```
tracker/engines.py        engine roster, the model x engine matrix, use-case
                          rankings, fidelity bands, per-issue notes
tracker/render_status.py  the model list (scores, architecture, licence) and
                          the whole HTML template
tracker/quants.py         GENERATED - measured quant ladders and KV geometry
tracker/build_quants.py   regenerates quants.py from the Hugging Face API
tracker/probe.py          refreshes watch-state.txt from the GitHub API
tracker/watch-state.txt   last polled state of every tracked issue
tracker/build.py          renders docs/index.html
tracker/watch.sh          local twice-daily watch loop
assets/                   social card source and output
docs/                     GENERATED, gitignored - the built site
```

`tracker/engines.py` and the `MODELS` list in `tracker/render_status.py` are the
two files worth reading first. Everything else is plumbing.

## How the numbers are derived

- **Weights** are summed file sizes from the linked Hugging Face repository —
  safetensors for MLX builds, GGUF for the rest. Measured, not estimated.
- **Bits per weight** is `bytes * 8 / total parameters`, so it is the effective
  figure rather than whatever the quant is named. Those diverge badly on MoE
  models: GLM-4.7's `UD-IQ1_S` is really 2.17 bpw, because the non-expert
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
- **Fit** assumes a 90% wired-memory limit plus ~10 GB of framework overhead. It
  answers "does this load", not "does this run well".

## Limits worth stating plainly

Nothing here has been benchmarked on this hardware by us. Benchmark scores are
vendor- or aggregator-reported. Issue states are a twice-daily snapshot. Every
memory and throughput figure is arithmetic over published specifications, not a
measurement. Treat the page as a shortlist filter and verify anything you intend
to spend money on.

If you have measured something on real hardware, that is the most valuable kind
of contribution — see [CONTRIBUTING.md](CONTRIBUTING.md).

## Older addresses

This repo's Pages site is canonical. Two earlier addresses on dreamingwell.com
still receive traffic and forward here in a single hop, carrying the query string
so shared deep links keep their selections:

- `/research/apple-llm-performance/`
- `/research/mlx-models/` — the address the original Reddit post used

`tracker/make_redirect.py` generates those stubs.

## Licence

MIT for the code. The benchmark figures and issue references belong to their
respective projects and are cited on the page.
