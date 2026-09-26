# Tokens per second

Design note for [issue #1](https://github.com/dreamingwell/apple-llm-performance/issues/1).
Written 2026-08-29.

## The question

> Please also add the option to show tok/sec. — @rdehuyss

> It was previously included, but the numbers were all just from people self
> reporting. I found them to be not very representative of average speeds. So I
> think this means we'd need a CLI tool that would run various LLMs and engines.
> But there are a lot of combinations. […] Anyone have a better idea of how to
> acquire reliable tokens per second? — @traviscollins

Yes. **Stop trying to acquire it.** Most of what a reader wants from a
tokens-per-second column can be *derived* from facts this page already holds,
and the part that cannot be derived should be collected as attributed
measurements rather than as reports.

## Why the self-reported numbers failed

Not because contributors were careless. Because a bare tokens-per-second figure
is not a fact about a model — it is a fact about a *run*, and the run has at
least six axes:

    model × engine (and version) × quantised build × chip × context × concurrency

Change any one and the number moves by more than the differences people were
using it to judge. This page already carries two proofs of that, and they are
now on the page as records rather than as prose:

- GLM-5.2 prefill on an M3 Ultra 512 GB is **845 tok/s** with oMLX's native DSA
  kernels compiled in and **about 29 tok/s** with the silent fallback that a
  plain `pip install` gives you. Same model, same chip, same day. A 29×
  spread between two correct measurements.
- Qwen3.8-27B on oMLX on an M3 Ultra was reported at **36.5 tok/s** and later at
  **24 tok/s**. Neither report states the build. On that chip the 8-bit MLX
  build is bounded by memory bandwidth at 27.8 tok/s and the 4-bit build at
  about 51, so 36.5 is either a 4-bit run or the MTP path emitting more than one
  token per weight read — and nobody can tell which from the report.

So the failure was structural. A collection policy that accepts a number without
the run that produced it will always produce an average of incommensurable
things. Averaging harder does not fix it.

## The options

### A. Rebuild crowd-sourced reporting, with a schema this time

Require chip, memory, engine version, exact quant, context and concurrency, and
reject anything short. This is not silly — the schema is most of what was
missing. But it does not solve trust (nobody can reproduce the run), it does not
solve coverage (the models nobody owns hardware for are exactly the ones the
buying decision turns on), and it needs a submission backend.

**Rejected as the primary mechanism.** Kept as a *secondary* one: see C.

### B. Build the benchmark matrix — a CLI that downloads and runs everything

The maintainer's own sketch, and the objection is correct. Costed against this
repository as it stands today:

- 16 text models, 8 text engines, 187 published quant builds
- **44.5 TB** to download the published builds once
- 475 build × engine pairs that any engine here could actually load
- 55 chip-and-memory configurations in the picker

That is roughly **26,000 runs** before you multiply by context length,
concurrency, or engine version — and the answer expires when any engine ships a
release. It also needs hardware nobody has: half the picker's configurations are
machines the maintainer does not own, so the matrix would be sparse in exactly
the places the ceiling matters most.

**Rejected.** Not because it is a bad idea but because it is the wrong first
step: it is the most expensive way to learn something the arithmetic already
tells you to two significant figures.

### C. Harvest published measurements, with provenance

Some projects publish their own measured figures on named hardware. ds4's
speed-bench README carries real Metal numbers for a specific machine, build and
context. Upstream issue threads carry regressions with before-and-after figures.
These are a different confidence class from crowd-sourced reports: they are
attributable, and the page already has a house rule that a claim resting on
someone else's measurement says whose.

**Adopted.** This is data the repository already had — it was sitting in prose
inside engine notes, unstructured and uncomparable.

### D. Derive a bound from memory bandwidth

Decoding one token at batch 1 reads the whole active weight set plus whatever
the model attends over in its KV cache, and reuses almost none of it next step.
Decode therefore waits on memory, and on Apple silicon peak memory bandwidth is
a published specification of the chip. So:

    tok/s ≤ bandwidth ÷ (build size × active ÷ total + KV per token × context)

Every term is already in this repository — `bw` in the chip table, the measured
`gb` of the chosen rung, `ACTIVE_PARAMS_B`, and `KV["bytes_per_token"]` derived
from each model's `config.json`.

**Adopted, as a ceiling and not as an estimate.** See the next section for why
that distinction is the whole design.

### E. A small CLI that measures one model the user already has

Not the matrix: a single command that attaches to a model and engine already
installed on the machine, runs a fixed prompt at fixed contexts, and emits a
`SPEEDS`-shaped record for a pull request. No downloads, no engine installation,
no backend — the submission channel is the one this repository already has.

**Deferred, and recommended as the next step.** Sketched at the end.

## Ceiling, not estimate — the one decision that matters

The tempting version of option D is to multiply the bound by an efficiency
constant and print the product as "estimated tok/s". Do not. That constant is
the only invented number in the whole chain, and it would be doing all the work
while looking like arithmetic.

The evidence says it would also be wrong. Of the three published decode
measurements on this page complete enough to check, real decode landed at
**19%, 26% and 32%** of the bound — all three sparse MoE on asymmetric quants.
A dense model on the same arithmetic would land far higher. There is no single
constant here, and pretending otherwise would convert an honest bound into a
dishonest prediction.

A bound is worth shipping on its own terms:

- It is a theorem about the hardware, not a claim about anybody's setup. It
  cannot be "not representative" because it does not claim to represent a run.
- It is decision-useful in the direction people actually need. "This model
  cannot exceed 9 tok/s on your machine" settles a purchase; "it might do 30"
  does not.
- It is computable for every model on the page, including the ones nobody has
  ever benchmarked — which is where a measurement programme is weakest and
  stays weakest.
- It is in the same confidence class as the memory-fit arithmetic the page
  already ships and already labels as arithmetic. No new epistemics.

And the gap between the bound and the measurements is not swept away — it is
rendered, as a table, so a reader can see how far under the bound real engines
land and decide how much to discount.

## Confidence classes

The page now distinguishes three, and never mixes them:

| Class | What it is | How it is marked | Where it comes from |
|---|---|---|---|
| **Measured** | Somebody else's run, with the machine, build and context it came off | Plain figure in a "Measured by others" block, with a link to the measurer | `SPEEDS` in `data/models/<id>.py` |
| **Derived** | Bandwidth ÷ bytes read per token, for the selected cluster | Always prefixed `≤`, always called a ceiling, never a bare number | `tracker/throughput.py` and its mirror in the page's JavaScript |
| **Rejected** | Self-reported figures with no run attached | Not carried | — |

An under-specified published measurement is still *measured* — it is somebody's
real number — but it is not comparable, so it is shown with "build not stated"
and excluded from the calibration table rather than quietly dropped. The two
Qwen3.8 records exist to make that visible.

## What shipped

- `data/machines.py` — the chip table, moved out of the JavaScript literal so
  Python can read `bw` too. One bandwidth table, not two.
- `tracker/throughput.py` — the formula, and the written statement of what it
  assumes and where it is wrong. The page's JavaScript mirrors the four lines of
  arithmetic; the file is the specification.
- `ACTIVE_PARAMS_B` on all 16 text models. `None` for GLM-5.3-Flash, which
  publishes expert counts but no active-parameter total — so it gets no ceiling
  rather than a guessed one.
- `SPEEDS` on five models: eight published measurements, each naming its
  measurer and linking to it.
- Validation: `ACTIVE_PARAMS_B` required for text models; every `SPEEDS` record
  checked for a known engine, a known chip, a real memory option, a measurer and
  a link; a warning when a decode figure lacks the build or the context; and a
  **plausibility check that rejects any decode figure above the bandwidth bound**
  unless the record declares speculative decoding or batching. That check would
  have caught a mistyped Qwen figure, and it is the reason a fabricated number is
  hard to land here.
- On the page: a `≤ N tok/s` column in the glance list, a decode-ceiling line
  and a ceiling column in each engine's context table, the measurements on each
  model card, and a "Tokens per second" reference panel carrying the formula,
  its seven failure modes, and the calibration table.

## Where the ceiling is wrong

Stated in full in `tracker/throughput.py` and on the page itself. In short: it is
a bound and not an estimate; sparse MoE at batch 1 does badly against it; it
assumes uniform bits per weight, which ds4's asymmetric routed quants and
Qwen3.8-Flash-Next's n-gram table both violate; it assumes the whole KV cache is
read, which the sparse-attention models do not do; it excludes expert-pruned
builds entirely, because pruning buys memory and not speed; speculative decoding
can legitimately beat it; pooling does not raise it; and it says nothing about
prefill, which is compute-bound.

## Deliberately not shipped

- **No efficiency constant, and no "estimated tok/s".** Argued above.
- **No prefill derivation.** Prefill is a batched matmul over the prompt. The
  bandwidth argument does not apply, and no honest arithmetic replaces it.
  Published prefill figures are shown; none is derived.
- **No submission backend.** Pull requests against `data/models/<id>.py` already
  work, are reviewable, and leave the provenance in git history. A form that
  writes to a database would lose the review step, which is the only thing that
  kept the bad numbers out.
- **No time-to-first-token, and no concurrency throughput.** TTFT is prefill plus
  scheduler behaviour; aggregate throughput under batching is a different
  quantity with a different bound. Both are worth having and neither is this
  change.

## The next step, if the maintainer wants one

A `tracker/bench.py` that measures what is already installed:

    python3 tracker/bench.py --model qwen38 --engine mlxlm \
        --build mlx-community/Qwen3.8-27B-4bit --context 8192

It would drive the engine's OpenAI-compatible endpoint (all eight text engines
here serve one), decode a fixed number of tokens from a fixed prompt at each
requested context, read the chip and memory from `sysctl`, and print a `SPEEDS`
record ready to paste into a model file — including the fields that make it
comparable, because it cannot omit them.

That is a few hundred lines and no backend. It does not solve coverage, and it
should not pretend to: it makes *one* good record easy to produce, and the
review process decides whether it lands. Two open questions for the maintainer
before it is worth writing:

1. **Should `bench.py` submissions be trusted more than a hand-written record?**
   They are still self-reported — the tool just makes them complete. My view:
   same class, better hygiene, and the bandwidth plausibility check applies to
   both.
2. **Should the glance column be the ceiling at 8k, or user-selectable
   context?** It is 8k today, stated in the legend. A control would be more
   honest about how much the number moves and is one more thing in the picker.
