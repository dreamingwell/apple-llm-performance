# Contributing

The page is only as good as its facts. Corrections are more welcome than
additions, and measurements are more welcome than either.

Everything renders from plain Python data structures, one file per record, so
most contributions are a few lines in one file. There are no dependencies:
`python3 tracker/validate.py` checks your change and `python3 tracker/build.py`
regenerates the site.

If you are an AI agent, read [AGENTS.md](AGENTS.md) instead — it is the same
information at the depth an agent needs, plus the rules that keep concurrent
contributions from colliding.

## Especially wanted

**New and useful models.** If open weights have shipped and the thing runs on
Apple silicon, we want it on the page. Adding one is a new file in
`data/models/` plus a line in each category it belongs to.

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

Everything about a model — architecture, licence, context, benchmark scores, the
summary paragraph, and its status on every engine — is in
`data/models/<id>.py`. One model, one file.

Keep the model-level `NOTE` engine-neutral. Anything true only of one runtime
belongs in that runtime's cell in `ENGINES`, or the two contradict each other as
engines change.

### Adding a model

1. Copy the closest existing `data/models/<id>.py` and fill it in: identity
   fields, `MODALITY`, `NOTE`, `SOURCES`, `PARAMS_B`, an `ENGINES` cell per
   engine that could load it, `BEST_ENGINE`, `QUANT_SOURCES`, and `KV`.
2. `python3 tracker/measure.py --model <id>` fills in `LADDER` from the Hugging
   Face API. Don't hand-write it.
3. Add a line to each `data/use_cases/*.py` `RANK` list the model has published
   numbers for. Leave it out of the others; the page dims those rows rather than
   guessing.
4. `python3 tracker/validate.py` then `python3 tracker/build.py`, and look at
   the card.

The `KV` figure counts only layers whose cache grows with context — see the KV
section of [AGENTS.md](AGENTS.md), which works through an example.

Watch two things. Parameter counts sometimes exclude part of the checkpoint —
Qwen3.8-Flash-Next is stated as 125B but ships 180B on disk because of a 51B
n-gram embedding table, and bits-per-weight has to be computed against what has
to be resident. And a published quant existing does not mean anything can load
it: `mlx-community` ships a `DeepSeek-V4-Flash-4bit` whose card says
`pip install mlx-lm`, but mlx-lm has no `deepseek_v4` model class. Check the
engine's architecture table or model directory, and check `config.json`'s
`model_type`, not the model card prose.

### Adding an engine

A new `data/engines/<id>.py` — identity, `MODALITIES`, `API_DETAIL`,
`QUANT_FAMILY`, `RELEASE_FEED`, `CROSS_ISSUES`, a `SITE` and `PROSE_ALIASES`
(the renderer links the first mention of each engine in each note to its site,
so you never hand-link an engine name), and a `DISPLAY_ORDER` that decides where
its tab sits — plus a cell in the `ENGINES` dict of every model it can load. The last part is the work; there is no way around describing each
model on the new engine.

### Adding a tracked issue

Add it to `data/issues/<owner>__<repo>.py` with a severity, a headline and a
sentence on why it matters, then cite its key from the relevant model's engine
cell or from that engine's `CROSS_ISSUES`. `tracker/probe.py` derives its
watchlist from that metadata, so it starts polling on the next run with no
second edit.

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
python3 tracker/validate.py    # must print "0 errors"
python3 tracker/build.py
python3 tools/check_output.py
```

That is the whole test suite, and it is what CI runs. `validate.py` checks every
record in `data/` and reports every problem it finds rather than the first.
`build.py` fails loudly on a malformed template and refuses to emit a page
containing control characters — a real bug that shipped once, from a Python
octal escape in a CSS rule. `check_output.py` catches a template field that
rendered as literal text instead of substituting.

Warnings from `validate.py` don't block anything. They flag a record that is
merely thin — a very short note, an issue tracked but cited nowhere.

Open the result and check the card you touched at more than one cluster size.
Several bugs in this page's history were only visible at a particular memory
size: a status badge reading "Runs" above four rows of "does not fit", or two
engines quoting different quantisations for the same machine.
