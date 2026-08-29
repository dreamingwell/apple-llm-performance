# AGENTS.md

Instructions for AI agents maintaining this repository.

Read this before touching anything. The repository is deliberately structured so
that many agents can work on it at once without conflicting, and most of that
structure only works if you follow the file-per-record rule below.

**The one rule that matters most:** one record, one file. A model, an engine, a
use case and an issue tracker each own exactly one file. If your change touches
one model, it should touch one file under `data/models/`. If you find yourself
editing a shared file to add a model, you have taken a wrong turn.

**Before you open a PR:**

```sh
python3 tracker/validate.py     # must print "0 errors"
python3 tracker/build.py        # must succeed
python3 tools/check_output.py   # checks the rendered page
```

That is exactly what CI runs, plus an import smoke test. Warnings from
`validate.py` do not block anything — they flag a record that is merely thin.

---

## 1. Why the structure is what it is

The data used to live in two files: a 1,500-line `engines.py` holding every
model's per-engine status, and a 1,900-line `render_status.py` holding both the
model list and the entire HTML template. Two agents adding two different models
conflicted every time, and an agent fixing CSS conflicted with an agent adding a
benchmark score.

Now:

```
data/
  models/<id>.py        one model: identity, scores, per-engine status, quant ladder, KV
  engines/<id>.py       one engine: what it is, its API, its website, its
                        cross-cutting issues
  use_cases/<id>.py     one "What for?" category and its curated ranking
  issues/<owner>__<repo>.py   tracked issues for one upstream repository
  pr_keys.py            which issue keys are pull requests (small, shared)
  machines.py           every M-series chip: bandwidth, memory options, Thunderbolt

tracker/
  registry.py           loads data/ and assembles it. The only file that knows the schema.
  validate.py           enforces the schema. CI runs this.
  render_status.py      the HTML template and the page's prose. No per-model data.
  bands.py              fidelity thresholds and per-model quant caveats
  throughput.py         the decode ceiling, and what it assumes
  build.py              renders docs/index.html
  measure.py            re-measures one model's quant ladder from Hugging Face
  probe.py              re-polls tracked issue states from GitHub
  watch-state.txt       last polled state of every tracked issue
  watch.sh              local twice-daily watch loop

tools/
  check_output.py       sanity-checks the rendered page

notes/
  tokens-per-second.md  why the page derives a ceiling and collects measurements

.github/workflows/
  validate.yml          the gate: validate, import-smoke, build, check output
  deploy.yml            builds and publishes Pages on push to main
  refresh.yml           re-polls issue states twice daily and commits changes
```

Conflict surface by task:

| Task | Files you touch |
|---|---|
| Add a model | `data/models/<new>.py`, and one line in one `data/use_cases/*.py` per category it belongs to |
| Correct a model's figure or prose | `data/models/<id>.py` only |
| Add or update a tracked issue | `data/issues/<repo>.py` only |
| Add an engine | `data/engines/<new>.py`, plus one cell in each `data/models/*.py` it can load |
| Change the UI | `tracker/render_status.py` only |
| Add a published throughput measurement | `data/models/<id>.py` only — see section 4b |
| Change the schema | `tracker/registry.py` **and** `tracker/validate.py`, in a commit of their own |

Two agents adding two models never touch the same file. Two agents adding issues
to two different upstream repos never touch the same file. That is the point.

---

## 2. Finding new models

There are two different jobs here, and they want different sources. **Discovery**
is "what shipped that we don't have yet". **Confirmation** is "can anything on
this page actually load it". Discovery sources are noisy and must never be
trusted on their own; confirmation sources are authoritative.

### Discovery: sources that announce new models

Every URL below was checked live on 2026-08-27. All are pollable without a key
unless noted. Recheck rather than assume — feeds move.

**Poll these first. They are structured, and they are where a new model shows up
before anyone writes about it.**

| Source | Query | What it is good for |
|---|---|---|
| Hugging Face trending | `https://huggingface.co/api/models?sort=trendingScore&direction=-1&limit=50` | The single highest-signal feed. A brand-new flagship trends within hours, at three-digit download counts. |
| Hugging Face, newest by format | `.../api/models?filter=mlx&sort=createdAt&direction=-1&limit=50` (also `filter=gguf`) | New *quants*, which is the thing that decides whether a model is usable here. |
| mlx-community uploads | `.../api/models?author=mlx-community&sort=createdAt&direction=-1&limit=50` | Apple-silicon-specific. If it appears here, someone has already converted it. |
| Ollama, newest | `https://ollama.com/search?o=newest` | A curated catalogue with a short list — parse `/library/<name>` hrefs. Very low noise. |
| llama.cpp arch list | `https://api.github.com/repos/ggml-org/llama.cpp/commits?path=src/llama-arch.cpp` | An architecture gaining support, from the authoritative file. Also names the arch string. |
| mlx-lm model classes | `https://api.github.com/repos/ml-explore/mlx-lm/commits?path=mlx_lm/models` | Same, for MLX. Note mlx-lm's *releases* lag badly (v0.31.3 is from April), so commits are the signal, not tags. |
| llama.cpp model PRs | `https://api.github.com/search/issues?q=repo:ggml-org/llama.cpp+label:model+is:pr+is:merged&sort=created&order=desc` | Support landing, with the discussion attached. Filter on `label:model` — a bare "add support" text search is mostly CUDA and CI PRs. |

**Where the labs announce.** Use these for a model too new to have quants, and
for the licence and the benchmark table, which the HF card often abbreviates.

- Qwen — https://qwen.ai/blog and https://qwenlm.github.io/blog/
- DeepSeek — https://api-docs.deepseek.com/news/news
- Z.ai / Zhipu (GLM) — https://z.ai/blog/<model-slug>; the HF org
  https://huggingface.co/zai-org is the more reliable poll
- Moonshot (Kimi) — https://moonshotai.github.io/
- MiniMax — https://www.minimax.io/news
- Google / Gemma — https://blog.google/technology/google-deepmind/
- Mistral — https://mistral.ai/news
- NVIDIA (Nemotron) — https://developer.nvidia.com/blog/category/generative-ai/
- Allen AI (OLMo, Molmo) — https://allenai.org/blog

**Community and aggregators.** Human signal: fastest to notice a model is
*interesting*, and the only place that reports whether it actually works. Never
take a figure from here — follow it to the primary source.

- **r/LocalLLaMA** is the highest-value one, and posts flaired *New Model* are
  the feed. `https://www.reddit.com/r/LocalLLaMA/new/.rss` works but rate-limits
  hard (HTTP 429 on a second request); back off, and do not build a tight poll
  on it.
- **Artificial Analysis** — https://artificialanalysis.ai/models — independent
  re-runs, so a cross-check on a lab's own claimed numbers.
- **LMArena** — https://lmarena.ai/leaderboard — Elo, which is not comparable
  with any benchmark on this page. Useful for noticing a model, useless for
  ranking one here.
- **Simon Willison** — https://simonwillison.net/tags/llm-release/ — annotated,
  and reliably flags when a release is less than it claims.
- **Hugging Face daily papers** — `https://huggingface.co/api/daily_papers` —
  early warning for an architecture, weeks before weights.

### When a tracked status changes, update the page in the same pass

`refresh.yml` polls every tracked issue twice a day and commits
`tracker/watch-state.txt`. The page turns that into an open/closed pill
automatically — but **the pill is not the update**. The prose around it still
asserts whatever was true when it was written, and a status of `blocked` or
`degraded` still reflects the old world.

So when you see a state change, act on it. Do not report it and wait to be
asked. A change that has been detected and not applied is worse than not polling
at all, because the page now carries a defect the maintainer knows is stale.

Work it through in this order:

1. **Read how it closed, not just that it closed.** `state_reason: completed` is
   a fix; `not_planned` is a won't-fix and changes nothing about the defect. Use
   the timeline API to find the PR or commit that closed it —
   `/issues/<n>/timeline` — and cite that in the `why`.
2. **Check the fix shipped, not just landed.** Merged to master is not in a
   release. If a packaged build still fails, the status is `degraded` with a
   "Master only" style label, not `works`.
3. **Do not upgrade a status on the strength of a closed issue alone.** If the
   defect was a performance figure, closing the issue does not produce a new
   figure. Say the old number is historical and the new one is unmeasured; do not
   invent one, and do not quietly leave the old one looking current.
4. **Follow every place the claim appears.** The engine cell's `status` and
   `label`, its `note`, the model-level `NOTE` if it repeats the point, any
   use-case `AXIS` that explained an exclusion, and the worked examples in
   `render_status.py`.
5. **Amend issue lists, never replace them.** A cell citing seven issues that
   you rewrite down to two silently drops five. `validate.py` warns about issues
   left cited nowhere — that warning is usually this mistake.
6. **A closed issue is often still worth citing.** It dates the fix, which is
   what a reader needs in order to know which build to get.

Then validate, build, commit and deploy.

Watch for one trap: a cross-reference in a timeline names an issue number
without its repository. `ml-explore/mlx-lm#1662` cross-references a
`#2042` that lives in `Blaizzy/mlx-vlm`, which is not an engine on this page.
Always resolve `source.issue.repository.full_name` before believing a
cross-reference is relevant.

### Confirmation: can anything here load it?

Discovery tells you a model exists. These say whether it belongs on the page,
and they overrule any announcement:

- llama.cpp: `src/llama-arch.cpp` — grep for the architecture name
- mlx-lm: the `mlx_lm/models/` directory listing — a missing `<model_type>.py`
  means mlx-lm cannot load it, whatever the quant's card claims
- vLLM Metal: `docs/supported_models.md`
- mflux, MLX-Audio, MLX-Video, DiffusionKit: the model tables in their READMEs
- Ollama: `https://ollama.com/library/<name>` 404s if absent

To go the other way — you have a name and want its quants — search by format:

```sh
curl -s "https://huggingface.co/api/models?search=<name>&filter=mlx&sort=downloads&direction=-1&limit=10"
curl -s "https://huggingface.co/api/models?search=<name>&filter=gguf&sort=downloads&direction=-1&limit=10"
```

`mlx-community/` and `ggml-org/` are first-party-ish. `unsloth/`, `bartowski/`
and `lmstudio-community/` are the serious third-party packagers. Those repo names
go straight into `QUANT_SOURCES`.

Match on `config.json`'s `model_type`, not the model's marketing name. As of
2026-08-27 `deepseek_v4`, `glm5_next`, `qwen4exp` and `minimax_m3` all have **no**
mlx-lm model class, while `mlx-community` publishes quants for several of them.

**Upstream feature requests** are the fourth state: not supported, but wanted.
Those are worth a row with a `blocked` cell and the issue cited.

A model earns a place if open weights have shipped **and** at least one engine on
this page can plausibly load it. A model with weights and no runtime still earns a
place if the gap is interesting — say so in the note and cite the tracking issue.

### Classifying it

**Modality** decides which engines it can pair with and which categories it can
appear in. One of `text`, `image`, `video`, `audio`.

**`PARAMS_B`** is total parameters in billions, not active. Beware: published
counts sometimes exclude part of the checkpoint. Qwen3.8-Flash-Next is stated as
125B but ships 180B on disk because of a 51B n-gram embedding table. Use what has
to be resident, because that is what bits-per-weight is divided by.

**Architecture** comes from `config.json`'s `model_type`, not from the model card
prose. This is how you avoid the trap in section 5.

### Getting benchmark scores

Prefer, in order: the model card's own table → the lab's blog or technical report
→ an aggregator such as Artificial Analysis → a reputable secondary writeup. Every
score needs a link in `SOURCES`.

Record the benchmark **name exactly**, including its version. `Terminal-Bench
2.0` and `Terminal-Bench 2.1` are different tests and the page refuses to rank
across them. If a card reports a range or several harnesses, take the one the
card leads with and say which in the note.

**Do not convert between benchmarks.** If a model reports SWE-bench Pro and the
category is ordered on SWE-bench Verified, record Pro. The page handles the
mismatch: it draws a bar only when two figures share a scale, and marks a row
with a dagger when they do not.

**If no benchmark exists, say so.** Image, video and audio models mostly have no
comparable published numbers. Leave `SCORES` empty and let the category's `AXIS`
explain that its ordering is editorial. An invented number is worse than none.

---

## 3. Adding a model, step by step

1. **Create `data/models/<id>.py`.** The `<id>` is lowercase alphanumeric, must
   match the filename, and never changes once published — it is the URL fragment
   (`#qwen38`) and people share those links. Copy the closest existing model as
   your template.
2. **Fill the identity fields.** `NAME`, `ARCH`, `LICENSE`, `CONTEXT`, `HF`,
   `PARAMS_B`, `ACTIVE_PARAMS_B`, `MODALITY`, `NOTE`, `SOURCES`.
   `ACTIVE_PARAMS_B` is the parameters read per decoded token — all of them for
   a dense model, the routed experts that fire plus everything shared for an
   MoE. It is what the decode ceiling divides bandwidth by, so it moves every
   throughput figure on the card. If the lab has not published a count, write
   `None` and say why in a comment; the page will show no ceiling rather than
   one derived from a guess. For a non-text model use
   `CONTEXT_LABEL` to relabel that spec — `Output`, `Coverage`, `Behaviour` — as
   "Context" is meaningless for a diffusion model.
3. **Write one `ENGINES` cell per engine that could load it.** Only engines whose
   modality matches; the validator enforces this. Each cell needs a `status`
   (`works` / `degraded` / `blocked` / `none`), a short `label` for the tab, a
   `note` explaining the status, and `issues` citing anything relevant.
4. **Set `BEST_ENGINE`** to the engine the card should open on. It must have a
   cell and must not be `none`.
5. **List `QUANT_SOURCES`**, then measure them:
   ```sh
   python3 tracker/measure.py --model <id>
   ```
   That writes `LADDER` into the model's own file and touches nothing else.
   Never hand-write a ladder.
6. **Fill `KV`.** For text models, count only layers whose cache grows with
   context — see section 4. For everything else, all three fields are `None`/`""`.
7. **Add it to the categories it has numbers for**, one line in each
   `data/use_cases/*.py` `RANK` list. Leave it out of categories where it
   publishes nothing; the page dims those rows rather than guessing.
8. **Validate and build.**

---

## 4. Deriving the KV figure

`bytes_per_token` is the fp16 KV cost of one token. Count **only layers whose
cache grows with context**:

- **Grouped-query attention:** `layers × kv_heads × head_dim × 2 × 2`
  (the `× 2`s are K-and-V, then fp16 bytes).
- **Latent attention** (MLA and the DSA variants): `layers × (kv_lora_rank +
  qk_rope_head_dim) × 2`. One compressed vector per layer, not separate K and V —
  which is why these models are so much cheaper per token.
- **Sliding-window layers** are bounded by the window, so they do not scale with
  context. Exclude them.
- **Linear / Mamba / KDA / Gated-DeltaNet layers** hold a fixed recurrent state.
  Exclude them.

Read `layer_types` or `full_attention_interval` in `config.json` to find how many
layers are actually full attention. Qwen3.8-27B has 64 layers but only 16 are
full attention, so its figure is `16 × 4 × 256 × 2 × 2 = 65,536` bytes — exactly
64 KiB/token. Getting this wrong by counting all 64 layers would overstate it
fourfold.

Put the reasoning in `derivation`. It is rendered on the page, and it is how the
next agent checks your arithmetic.

---

## 4b. Tokens per second

Two kinds of number, never mixed. Read `notes/tokens-per-second.md` before
adding either; it is the design argument, and this is the operating rule.

**Derived: the decode ceiling.** `tracker/throughput.py` divides the chip's peak
memory bandwidth by the bytes an engine must read to emit one token. It is an
upper bound and it is rendered as one — always prefixed `≤`, always called a
ceiling. Do not multiply it by an efficiency factor and call the product an
estimate. There is no such constant: the measurements collected here land
between 19% and 32% of the bound, and a dense model would land far higher.

**Measured: `SPEEDS`.** Somebody else's run, with the run attached:

```python
SPEEDS = [
 {'engine': 'ds4', 'chip': 'm5max', 'mem_gb': 128,
  'build': 'DeepSeek-V4-Flash-IQ2XXS-...', 'gb': 86.7, 'context': 2048,
  'decode_tps': 39.4, 'prefill_tps': 790,
  'who': 'ds4 speed-bench README',
  'url': 'https://github.com/antirez/ds4/blob/main/speed-bench/README.md',
  'note': 'why this figure is what it is, and what it does not cover'},
]
```

`engine` must have a cell in this model's `ENGINES`; `chip` must be a key in
`data/machines.py`; `who` and `url` are mandatory, because a measurement with no
measurer is a rumour. `build` and `context` are optional to the validator and
essential in practice — without them the record cannot be compared with
anything, and `validate.py` warns to say so.

Three rules that have already earned their place:

1. **Never invent a figure to fill a gap.** A model with no measurement gets its
   ceiling and nothing else. That is a complete answer.
2. **A figure above the bandwidth bound is an error unless the record says
   `speculative` or `batched`.** `validate.py` enforces this. If your record
   trips it, check the build size and the parameter counts before adding the
   flag — the flag is for MTP and draft heads, not for making the check quiet.
3. **Keep the under-specified records.** The two Qwen3.8 rows name only the chip
   and are kept deliberately: they are the page's evidence for why a bare
   tokens-per-second number is worth nothing. Do not tidy them away.

---

## 5. Pitfalls — every one of these has already happened here

**A published quant does not mean anything can load it.** `mlx-community` ships
`DeepSeek-V4-Flash-4bit` whose card says `pip install mlx-lm`, but mlx-lm has no
`deepseek_v4` model class. Always check the engine's architecture table or model
directory, and check `config.json`'s `model_type` — not the card prose.

**A quant's name is not its bits per weight.** GLM-5.2's `UD-IQ1_S` is really
2.33 bpw, because the non-expert tensors are carried at higher precision. This is
why ladders are measured, never estimated.

**Bits per weight is meaningless for media checkpoints.** They bundle a
transformer with text encoders and a VAE. Dividing repo bytes by the
transformer's parameter count gave LTX-2 a figure of *65 bits per weight*. Media
rungs use `kind="native"`, carry no `bpw`, and get no fidelity band.

**Do not rank across benchmarks.** See section 2. The page's central argument is
that you cannot, and a bar comparing a GDPval Elo of 1554 to a percentage would
undermine everything else on it.

**Do not rank a model on a benchmark that does not measure the job.** Nemotron
3.5 Lightning was once ranked for *agentic* work on MMLU Pro, a general-knowledge
test. That handed a model with no published agentic score a 94% agentic bar.

**Framework overhead is modality-dependent.** ~10 GB for an LLM server holding a
paged KV pool; ~1.5 GB for an image or audio runtime. A flat 10 GB made a 310 MB
TTS model report "10 GB resident".

**Only list issues that apply on Apple silicon.** Upstream trackers are dominated
by CUDA, ROCm and Vulkan reports. Including them makes the lists useless.

This is the rule this repo has broken worst. Every one of the four llama.cpp
issues once cited against DeepSeek V4 Flash was a CUDA report from a Windows or
Linux box with an RTX card, and together they were the stated reason to prefer a
different engine on a Mac. A reader on Reddit spotted it before we did.

So check, mechanically, every time. llama.cpp's issue template has `### GGML
backends`, `### Operating systems` and `### Hardware` fields — read all three
from the issue body before citing it:

```sh
gh api repos/ggml-org/llama.cpp/issues/<n> --jq .body | head -20
```

Of 25 open DeepSeek V4 Flash issues on llama.cpp, exactly one was on Metal. The
volume of an upstream tracker tells you nothing about Apple silicon, and a long
issue list is not evidence — it is usually a filtering failure.

**Verify an issue is what you think it is.** `jundot/omlx#2137` was cited here as
a custom-kernel warning. It is actually a closed GLM-5.2 prefill regression. Read
the issue.

**Engine names in prose are auto-linked — don't hand-link them.** Every engine
carries a `SITE` and a `PROSE_ALIASES` list, and the renderer links the first
mention of each engine in each block of prose to that site. Writing your own
`[mlx-lm](https://…)` is not wrong (a hand-written link always wins) but it is
redundant, and it will go stale when the engine moves. Just write the name.

Two consequences worth knowing. An alias is matched only as a whole token, so
`ds4-server` and `mlx-lm.server` are deliberately left alone — they are binaries,
not the project. And bare **`vLLM` is not an alias for vLLM Metal**: in these
notes it means upstream vLLM, and aliasing it would link six correct references
to the wrong project. If you add an engine whose short name is ambiguous like
that, leave it out of `PROSE_ALIASES` and write the full name in the prose.

**Prose goes stale against a ladder that re-measures itself.** `LADDER` is
regenerated from Hugging Face; the notes beside it are hand-written and stay
frozen. Two contradictions sat on the page for months: `gemma4` claimed no 4-bit
MLX quant of the 31B existed while its own ladder listed two, and `v4pro` claimed
nobody had published a PRO conversion while listing a 4-bit at 837 GB. Both were
true when written.

So whenever you touch a model, read its notes against its ladder and its issue
states, not just against the thing you came to change. This is not lintable — a
regex cannot tell "no `deepseek_v4` model class" from "no 4-bit quant", and one
that tries produces a dozen false positives for every real hit. It is a habit,
and it is the reason the maintenance procedure above says to follow a claim
through every place it appears.

**Never change a model's `id`.** It is the deep-link fragment.

**Do not commit `docs/`.** It is generated and gitignored. CI builds and deploys
it; committing it would conflict on every parallel PR.

**Do not hand-edit `LADDER`.** Run `tracker/measure.py`.

**Bits per weight is an average, and the decode ceiling assumes it is not.** The
ceiling scales a build's size by `active / total`, which is only the bytes read
per token if the whole checkpoint is quantised the same way. ds4's builds are
not — the labels say so: `IQ2XXS-w2Q2K-AProjQ8-SExpQ8-OutQ8` is 2-bit routed
experts with Q8 attention projections, shared experts and output. Those models
read more per token than the arithmetic says and their real ceiling is lower.
Qwen3.8-Flash-Next is dragged the other way by a 51B n-gram table that is looked
up rather than streamed.

**Expert pruning buys memory, not speed.** A REAP build deletes experts the
router was not going to pick, so per-token traffic barely moves: Kimi K3's
349.67 GB and 451.42 GB builds decode at the same rate. Pruned rungs therefore
get no ceiling at all, and a `SPEEDS` record naming a pruned build is exempt
from the bandwidth check.

**Escaping traps in `render_status.py`.** The HTML lives in a `str.format`
template, so every literal `{` or `}` in CSS or JS must be doubled. And never
write `\"` inside it — the escape is consumed twice, once by the Python string
and once by the template, and it silently emits broken JS. Use single-quoted JS
strings instead. A CSS `content: "\2212"` was parsed by Python as an *octal*
escape and shipped a control character to the page; the build now refuses to emit
any C0/C1 character.

---

## 6. How the UI is laid out

One page, two views, routed by the URL fragment.

**List view** (no fragment): header, the CPU/memory/units picker, then "Models at
a glance" — one row per model, filtered to the selected category's modality. Each
row shows a bar behind the name scaled against the category leader, a status
pill, the engine that wins for the current cluster, the chosen build's size, and
the memory left over.

**Detail view** (`#<model-id>`): the picker, a Back control, then one model card,
then the reference panels. A second Back control sits below the card and scrolls
to the picker.

**A model card** is a head — name, verdict, architecture/licence/output, the
best-fit line, the note, sources, and collapsed benchmark scores — above a
vertical rail of engine tabs. Each engine pane shows that engine's interface,
format, API and licence; the build chosen for the current cluster; what it costs
resident and what is left; a fidelity warning when the build is below full
precision; a table of concurrent contexts (text models only); the engine-specific
note; and the tracked issues.

**Blocked engines show only the reason and the issues** — no build, no size, no
fidelity band, no context table. Quoting memory arithmetic for something that
cannot load is noise.

Everything cluster-dependent is computed in the browser from the payload embedded
in each row and card, so changing the picker never reloads the page. The fragment
is the view state, which makes deep links, the browser Back button and the
on-page controls one mechanism.

---

## 7. Working alongside other agents

- **One PR, one concern.** A model addition and a UI change do not belong
  together; they touch different files for different reasons and a reviewer needs
  to judge them separately.
- **Never reformat a file you are not changing.** A whole-file reformat turns a
  one-line diff into a conflict for everyone else.
- **Rebase rather than merge** when your branch falls behind. The per-record
  layout means real conflicts are rare; if you hit one, it is usually two agents
  editing the same model, and the right answer is to read both versions rather
  than take yours.
- **Do not regenerate what you did not change.** `tracker/measure.py --model <id>`
  touches one file. Running it over everything rewrites 23 files and conflicts
  with every open PR.
- **If two categories disagree about a model, that is fine.** A model can lead
  coding and be absent from terminal work. Do not "fix" it by adding it
  everywhere.
- **State uncertainty in the data.** `status: "degraded"` with a note saying what
  is unverified is a better contribution than a confident `works` you cannot
  support.

---

## 8. House style for the prose

The notes are the reason to read this page rather than a spec sheet.

- Say what breaks and what it costs, not that something is "problematic".
- Prefer the number to the adjective.
- Where a claim rests on someone else's measurement, say whose.
- Where something is unverified, say so.
- Write for someone deciding how to spend money on hardware.
- No marketing language, and no hedging that carries no information.

---

## 9. Validation reference

`tracker/validate.py` enforces, and CI fails on, all of the following:

- ids are lowercase alphanumeric and match their filename
- modalities are known, and a model only has cells for engines that share its modality
- statuses are `works` / `degraded` / `blocked` / `none`
- every cell has a label and a note
- every cited issue key exists in `data/issues/` and is well-formed
- `BEST_ENGINE` exists in `ENGINES` and is not `none`
- `PARAMS_B` is present and non-zero
- `SOURCES` is non-empty and every entry is `(label, url)`
- ladders are ordered largest-first, `quant` rungs carry a believable `bpw`
  (0.5–20), `pruned` and `native` rungs carry none
- `KV` has exactly the three expected keys; only text models declare a per-token
  cost; a declared cost has a derivation and a max context
- text models declare `ACTIVE_PARAMS_B`; it is positive and not larger than
  `PARAMS_B`, or it is `None` (a warning, not an error); non-text models do not
  declare it at all
- every `SPEEDS` record names a known engine that has a cell in this model, a
  known chip from `data/machines.py`, a memory option that chip was sold with, a
  measurer and a URL, and carries at least one of `decode_tps` / `prefill_tps`
- a `SPEEDS` decode figure above what the chip's bandwidth allows for that build
  at that context is an **error** unless the record declares `speculative` or
  `batched` — the one check that makes a fabricated figure hard to land
- `data/machines.py` chips have a positive `bw`, an ascending deduplicated `mem`
  list, a `gen` that appears in `GENS`, and a Thunderbolt port count
- `DISPLAY_ORDER` is present and unique for engines and use cases
- every engine has a `SITE` URL and a non-empty `PROSE_ALIASES`, and no two
  engines claim the same alias — an ambiguous name would link to the wrong engine
- use-case ranks cite known models of the matching modality, with no duplicates
- issue severities are `critical` / `high` / `medium` / `low` and every issue has
  a stated consequence
- `pr_keys.py` only lists keys that exist

Warnings, which do not fail the build: a very short note, a missing ladder for a
family an in-scope engine loads, an issue tracked but cited nowhere, a modality
with no models or no category, and an alias that is neither the engine's own name
nor used in any note (which means it will never link, and is usually a typo).
