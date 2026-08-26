# Contributing

The page is only as good as its facts. Corrections are more welcome than
additions, and measurements are more welcome than either.

Everything renders from plain Python data structures, so most contributions are
a few lines in one file. `python3 tracker/build.py` regenerates the site with no
dependencies and no network access.

## Especially wanted

**New and useful models.** If open weights have shipped and the thing runs on
Apple silicon, we want it on the page. Adding one touches five files and is
described below.

**Numbers measured on real hardware.** Nothing on this page has been benchmarked
on Apple silicon by us — it is all published specifications and arithmetic. If
you have run one of these models on a Mac and have tokens/second, a peak
resident figure, or a context ceiling you actually hit, that is the single most
valuable thing you can add. Say which chip, how much memory, which engine
version and which exact quant.

**Corrections where the page is wrong about support.** The failure mode here is
concluding "blocked" from a missing quant when the real blocker is elsewhere, or
the reverse. If a model loads for you on an engine the page says it doesn't,
that's a bug worth an issue.

## Opening an issue

Useful issues usually contain one of:

- a wrong figure, with the source for the right one
- a model that should be listed
- an engine that should be listed
- an architecture that has gained or lost support upstream
- a measured result

## Common changes

### Correcting a figure or a note

Model-level facts — architecture, licence, context, benchmark scores, the
summary paragraph — live in the `MODELS` list in `tracker/render_status.py`.

Engine-specific facts live in `MATRIX` in `tracker/engines.py`, keyed
`[model_id][engine_id]`. Each cell carries its status, the prose explaining that
status, and the issues cited for it.

Keep model-level notes engine-neutral. Anything true only of one runtime belongs
in that runtime's cell, or the two contradict each other as engines change.

### Adding a model

1. `tracker/build_quants.py` — add the parameter count to `PARAMS`, the source
   repositories to `SOURCES`, and the KV geometry to `KV`. The KV entry counts
   only layers whose cache grows with context; read the comment above the table.
2. Run `python3 tracker/build_quants.py` to regenerate `tracker/quants.py`.
3. `tracker/render_status.py` — add an entry to `MODELS`.
4. `tracker/engines.py` — add a `MATRIX` row with a cell per engine, add the
   model to `BEST`, and place it in the `USE_CASES` rankings it has published
   numbers for. Leave it out of rankings where it hasn't; the page dims those
   rows rather than guessing.
5. `python3 tracker/build.py` and check the card.

Watch two things. Parameter counts sometimes exclude part of the checkpoint —
Qwen3.8-Flash-Next is stated as 125B but ships 180B on disk because of a 51B
n-gram embedding table, and bits-per-weight has to be computed against what has
to be resident. And a published quant existing does not mean anything can load
it: `mlx-community` ships a `DeepSeek-V4-Flash-4bit` whose card says
`pip install mlx-lm`, but mlx-lm has no `deepseek_v4` model class. Check the
engine's architecture table or model directory, and check `config.json`'s
`model_type`, not the model card prose.

### Adding an engine

Add an entry to `ENGINES` in `tracker/engines.py` — including its `api_detail`
block — a `FAM` mapping for the quant format it loads, a `CROSS_BY_ENGINE` list,
a `RELEASE_FEEDS` entry, and a cell in every `MATRIX` row. The last part is the
work; there is no way around describing each model on the new engine.

### Adding a tracked issue

Add it to `EMETA` in `tracker/engines.py` with a severity, a headline and a
sentence on why it matters, then cite its key from the relevant `MATRIX` cell or
`CROSS_BY_ENGINE` list. `tracker/probe.py` derives its watchlist from that
metadata, so it will start polling on the next run with no second edit.

Only list issues that apply on Apple silicon. Upstream threads are dominated by
CUDA, ROCm and Vulkan reports that are irrelevant here, and including them makes
the lists useless.

## House style for the prose

The notes are the reason to read the page rather than a spec sheet, so:

- Say what breaks and what it costs, not that something is "problematic".
- Prefer the number to the adjective.
- Where a claim rests on someone else's measurement, say whose.
- Where something is unverified, say that too.

## Before you send it

```sh
python3 tracker/build.py
```

That is the whole test suite. It fails loudly on a malformed template, and it
refuses to emit a page containing control characters — a real bug that shipped
once, from a Python octal escape in a CSS rule.

Open the result and check the card you touched at more than one cluster size.
Several bugs in this page's history were only visible at a particular memory
size: a status badge reading "Runs" above four rows of "does not fit", or two
engines quoting different quantisations for the same machine.
