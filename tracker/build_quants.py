"""Generate quants.py: a measured quant ladder per model per format family.

One rung per useful size point, with effective bits-per-weight computed from the
actual file bytes rather than read off the quant's name - the two diverge badly
on MoE models, where GLM-4.7's "UD-IQ1_S" is really 2.17 bpw because the
non-expert tensors are carried at higher precision.

Rungs whose loss is structural rather than numeric (REAP expert pruning) are
marked kind="pruned" and carry no bpw, because bits-per-surviving-weight says
nothing about the experts that were deleted.
"""
import json, os, urllib.request, re, collections, sys
from pprint import pformat

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "quants.py")

PARAMS = {"glm47":358,"glm47f":31,"glimmer":30,"nemolight":30,"gptoss":120,
 "gemma4":30.7,"qwen38":27.8,"m3":428,"v4flash":284,"glm52":744,"v4pro":1600,
 "kimik3":2780,"qwenmax":2446,
 # generative media
 "flux2k4":4,"flux2k9":9,"zimage":6,"ltx2":19,
 "kokoro":0.082,"magpie":0.357,"voicechat":11,"mmmusic3":7,"qcnext":80,
 # Qwen counts Flash-Next as 125B; the safetensors total is 180B because the
 # 51B n-gram embedding table is part of the checkpoint. Weights on disk are what
 # has to be resident, so bits-per-weight is computed against 180B.
 "q38fnext":180}

# format family -> list of repos to harvest, in preference order
SOURCES = {
 "glm47":  {"gguf":["unsloth/GLM-4.7-GGUF"], "mlx":["mlx-community/GLM-4.7-8bit","mlx-community/GLM-4.7-6bit","mlx-community/GLM-4.7-4bit","mlx-community/GLM-4.7-REAP-50-mxfp4"]},
 "glm47f": {"gguf":["unsloth/GLM-4.7-Flash-GGUF","ggml-org/GLM-4.7-Flash-GGUF"], "mlx":["mlx-community/GLM-4.7-Flash-8bit","mlx-community/GLM-4.7-Flash-6bit","mlx-community/GLM-4.7-Flash-5bit","mlx-community/GLM-4.7-Flash-4bit"]},
 "glimmer":{"gguf":["unsloth/Muse-Glimmer-30B-GGUF"], "mlx":["mlx-community/Muse-Glimmer-30B-8bit","mlx-community/Muse-Glimmer-30B-6bit","mlx-community/Muse-Glimmer-30B-4bit","mlx-community/Muse-Glimmer-30B-mxfp4"]},
 "nemolight":{"gguf":["ggml-org/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-GGUF","unsloth/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-GGUF"], "mlx":["mlx-community/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-8bit","mlx-community/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-4bit","mlx-community/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-mxfp4"]},
 "gptoss": {"gguf":["ggml-org/gpt-oss-120b-GGUF"], "mlx":["lmstudio-community/gpt-oss-120b-MLX-8bit","inferencerlabs/openai-gpt-oss-120b-MLX-Q6","mlx-community/gpt-oss-120b-MXFP4-Q8"]},
 "gemma4": {"gguf":["unsloth/gemma-4-31B-it-GGUF","unsloth/gemma-4-31B-it-qat-GGUF"], "mlx":["mlx-community/gemma-4-31b-it-8bit","mlx-community/gemma-4-31B-it-qat-4bit","mlx-community/gemma-4-31b-it-4bit"]},
 "qwen38": {"gguf":["unsloth/Qwen3.8-27B-GGUF"], "mlx":["mlx-community/Qwen3.8-27B-8bit","lmstudio-community/Qwen3.8-27B-MLX-6bit","lmstudio-community/Qwen3.8-27B-MLX-5bit","mlx-community/Qwen3.8-27B-4bit","mlx-community/Qwen3.8-27B-OptiQ-4bit"]},
 "m3":     {"gguf":["unsloth/MiniMax-M3-GGUF"], "mlx":["pipenetwork/MiniMax-M3-MLX-8bit","pipenetwork/MiniMax-M3-MLX-6bit","mlx-community/MiniMax-M3-4bit","pipenetwork/MiniMax-M3-MLX-mixed-3_6bit","pipenetwork/MiniMax-M3-MLX-3bit"]},
 "v4flash":{"gguf":["unsloth/DeepSeek-V4-Flash-0731-GGUF"], "mlx":["mlx-community/deepseek-ai-DeepSeek-V4-Flash-8bit","mlx-community/DeepSeek-V4-Flash-4bit","inferencerlabs/DeepSeek-V4-Flash-MLX-Q2.8-INF","mlx-community/DeepSeek-V4-Flash-2bit-DQ"], "ds4":["antirez/deepseek-v4-gguf"]},
 "glm52":  {"gguf":["unsloth/GLM-5.2-GGUF"], "mlx":["mlx-community/GLM-5.2-DQ4plus-q8","mlx-community/GLM-5.2-4bit","mlx-community/GLM-5.2-mxfp4","pipenetwork/GLM-5.2-MLX-mixed-3_6bit"], "ds4":["antirez/glm-5.2-gguf"]},
 "v4pro":  {"gguf":["unsloth/DeepSeek-V4-Pro-0813-GGUF"], "mlx":["mlx-community/DeepSeek-V4-Pro-4bit","inferencerlabs/DeepSeek-V4-Pro-Preview-MLX-Q2.8-INF"], "ds4":["antirez/deepseek-v4-gguf"]},
 "kimik3": {"gguf":["unsloth/Kimi-K3-GGUF"], "mlx":["pipenetwork/Kimi-K3-REAP73-MLX-mxfp4-q8","pipenetwork/Kimi-K3-REAP80-MLX-mxfp4-q8"]},
 "qwenmax":{"gguf":["unsloth/Qwen3.8-2.4T-A95B-GGUF",
                    "hellohazime/Qwen3.8-2.4T-A95B-REAP-256GB-GGUF",
                    "hellohazime/Qwen3.8-2.4T-A95B-REAP-512GB-GGUF"],
            "mlx":["kernelpool/Qwen3.8-2.4T-A95B-3bit-UVMAX",
                   "pipenetwork/Qwen3.8-2.4T-A95B-MLX-reap50-3bit",
                   "pipenetwork/Qwen3.8-2.4T-A95B-MLX-reap60-3bit",
                   "pipenetwork/Qwen3.8-2.4T-A95B-MLX-reap75-4bit"]},
 "qcnext": {"gguf":["unsloth/Qwen3-Coder-Next-GGUF"],
            "mlx":["mlx-community/Qwen3-Coder-Next-8bit","mlx-community/Qwen3-Coder-Next-6bit",
                   "mlx-community/Qwen3-Coder-Next-5bit","mlx-community/Qwen3-Coder-Next-4bit",
                   "nightmedia/Qwen3-Coder-Next-mxfp4-mlx"]},
 "q38fnext":{"gguf":["unsloth/Qwen3.8-Flash-Next-GGUF"], "mlx":[]},
 # --- generative media: weights are published as-is, so the "ladder" is usually
 # one or two precisions rather than a dozen quant tiers ---
 "flux2k4": {"gguf":["unsloth/FLUX.2-klein-4B-GGUF"], "mlx":["black-forest-labs/FLUX.2-klein-4B"]},
 "flux2k9": {"gguf":[], "mlx":["black-forest-labs/FLUX.2-klein-9B"]},
 "zimage":  {"gguf":[], "mlx":["Tongyi-MAI/Z-Image-Turbo"]},
 "ltx2":    {"gguf":[], "mlx":["Lightricks/LTX-2.3-fp8","Lightricks/LTX-2.3"]},
 "kokoro":  {"gguf":[], "mlx":["mlx-community/Kokoro-82M-bf16","mlx-community/Kokoro-82M-8bit",
                               "mlx-community/Kokoro-82M-4bit"]},
 "magpie":  {"gguf":[], "mlx":["aufklarer/Magpie-TTS-Multilingual-357M-MLX-8bit",
                               "aufklarer/Magpie-TTS-Multilingual-357M-MLX-4bit"]},
 "voicechat":{"gguf":[], "mlx":["mlx-community/NemotronLabs-VoiceChat-11B-8bit",
                                "mlx-community/NemotronLabs-VoiceChat-11B-4bit"]},
 "mmmusic3":{"gguf":[], "mlx":["mlx-community/MiniMax-Music3-bf16","mlx-community/MiniMax-Music3-8bit",
                               "mlx-community/MiniMax-Music3-4bit"]},
}

# Media checkpoints bundle a transformer with text encoders and a VAE, so
# dividing repo bytes by the transformer's parameter count is meaningless - LTX-2
# came out at 65 "bits per weight" that way. These models carry the precision
# their repo states instead, and no fidelity band.
MEDIA = {"flux2k4", "flux2k9", "zimage", "ltx2", "kokoro", "magpie", "voicechat", "mmmusic3"}

DRAFT = re.compile(r"(mmproj|^mtp-|-mtp|dflash|dspark|eagle3|imatrix|Qwen3\.5-\d|MTP)", re.I)

# Some repos hold more than one checkpoint - antirez/deepseek-v4-gguf carries both
# Flash and PRO - so a family needs a name filter or each model absorbs the other's
# files and the bits-per-weight figure comes out nonsense.
ONLY = {("v4flash", "ds4"): re.compile(r"V4-Flash", re.I),
        ("v4pro", "ds4"): re.compile(r"V4-Pro", re.I)}
PRUNED = re.compile(r"(REAP|reap\d)", re.I)


def pruned_repo(repo):
    return bool(PRUNED.search(repo))


def api(u):
    try:
        return json.load(urllib.request.urlopen(u))
    except Exception as e:
        print(f"  ERR {u}: {e}", file=sys.stderr)
        return []


def gguf_rungs(repo, mid, only=None):
    g = collections.defaultdict(int)
    for f in api(f"https://huggingface.co/api/models/{repo}/tree/main?recursive=true"):
        p = f.get("path", "")
        if not p.endswith(".gguf"):
            continue
        base = re.sub(r"\.gguf$", "", re.sub(r"-\d{5}-of-\d{5}", "", p.split("/")[-1]))
        if DRAFT.search(base):
            continue
        if only and not only.search(base):
            continue
        g[base] += f.get("size", 0)
    out = []
    for k, v in g.items():
        gb = v / 1e9
        if gb < 1:
            continue
        pr = bool(PRUNED.search(k)) or pruned_repo(repo)
        kind = "native" if mid in MEDIA else ("pruned" if pr else "quant")
        out.append({"label": k, "repo": repo, "gb": round(gb, 1), "kind": kind,
                    "bpw": None if kind != "quant" else round(gb * 8 / PARAMS[mid], 2)})
    return out


def mlx_rungs(repo, mid):
    tot = sum(f.get("size", 0) for f in
              api(f"https://huggingface.co/api/models/{repo}/tree/main?recursive=true")
              if f.get("path", "").endswith(".safetensors"))
    gb = tot / 1e9
    if gb < 0.05:              # TTS models are hundreds of megabytes, not gigabytes
        return []
    pruned = bool(PRUNED.search(repo))
    kind = "native" if mid in MEDIA else ("pruned" if pruned else "quant")
    return [{"label": repo.split("/")[-1], "repo": repo, "gb": round(gb, 2), "kind": kind,
             "bpw": None if kind != "quant" else round(gb * 8 / PARAMS[mid], 2)}]


def thin(rungs, keep=9):
    """Drop rungs within 4% of a larger sibling - same fit, no extra information."""
    rungs = sorted(rungs, key=lambda r: -r["gb"])
    out = []
    for r in rungs:
        if out and r["gb"] > out[-1]["gb"] * 0.97 and r["kind"] == out[-1]["kind"] and r["gb"] > 1:
            continue
        out.append(r)
    if len(out) <= keep:
        return out
    # keep the extremes and spread the rest evenly across the size range
    idx = sorted({0, len(out) - 1} | {round(i * (len(out) - 1) / (keep - 1)) for i in range(keep)})
    return [out[i] for i in idx]


LADDERS = {}
for mid, fams in SOURCES.items():
    LADDERS[mid] = {}
    for fam, repos in fams.items():
        rungs = []
        for repo in repos:
            rungs += (gguf_rungs(repo, mid, ONLY.get((mid, fam)))
                      if fam in ("gguf", "ds4") else mlx_rungs(repo, mid))
        LADDERS[mid][fam] = thin(rungs)
    print(f"== {mid}")
    for fam, rs in LADDERS[mid].items():
        if not rs:
            continue
        print(f"  {fam}:")
        for r in rs:
            b = f"{r['bpw']:5.2f} bpw" if r["bpw"] else "  pruned "
            print(f"    {r['gb']:8.1f} GB  {b}  {r['label'][:64]}")

with open(OUT, "w") as f:
    f.write('"""Measured quant ladders. Generated by build_quants.py - do not hand-edit.\n\n'
            'gb is summed file bytes from the HF repo; bpw is gb*8/total-params, so it is\n'
            'the effective bits per weight rather than whatever the quant is named.\n'
            'kind="pruned" marks REAP expert-pruned builds, where the loss is structural\n'
            'and a bits-per-weight figure would be misleading.\n"""\n\n')
    f.write("PARAMS = " + pformat(PARAMS) + "\n\n")
    f.write("LADDERS = " + pformat(LADDERS) + "\n")
print("\nwrote quants.py")


# ---------------------------------------------------------------------------
# KV cache cost per token, derived from each model's published config.json.
#
# Only layers whose cache grows with context are counted. Sliding-window layers
# are bounded by the window, and linear/Mamba/KDA layers hold a fixed-size
# recurrent state, so neither scales with context and neither belongs in a
# per-token figure. Latent-attention models (MLA and the DSA variants) store one
# compressed vector of kv_lora_rank + qk_rope_head_dim per layer rather than a
# separate K and V, which is why they are so much cheaper per token.
# ---------------------------------------------------------------------------

def gqa(layers, kv_heads, head_dim):
    return layers * kv_heads * head_dim * 2 * 2      # K and V, fp16


def mla(layers, lora, rope):
    return layers * (lora + rope) * 2               # one compressed latent, fp16


KV = {
 # mid:      bytes/token,                    max ctx,   how it was derived
 "glm47":    (gqa(92, 8, 128),               202752, "92 layers x 8 KV heads x 128, full attention throughout"),
 "glm47f":   (mla(47, 512, 64),              202752, "47 layers of latent attention, kv_lora_rank 512 + 64 rope"),
 "glimmer":  (gqa(13, 2, 128),               131072, "13 of 52 layers are full attention; the other 39 are windowed at 2048"),
 "nemolight":(gqa(6, 2, 128),                262144, "hybrid Mamba-Transformer: only the handful of attention layers grow, the SSM state is fixed"),
 "gptoss":   (gqa(18, 8, 64),                131072, "18 of 36 layers are full attention, alternating with a 128-token window"),
 "gemma4":   (gqa(10, 16, 256),              262144, "10 of 60 layers are full attention, the rest windowed at 1024"),
 "qwen38":   (gqa(16, 4, 256),               262144, "16 of 64 layers are full attention, one in every 4; the other 48 are linear"),
 "m3":       (gqa(60, 4, 128),              1048576, "60 layers x 4 KV heads x 128, full attention throughout"),
 "v4flash":  (mla(43, 512, 64),             1048576, "43 layers of DSA latent attention, 512 + 64 rope"),
 "glm52":    (mla(78, 512, 64),             1048576, "78 layers of DSA latent attention, 512 + 64 rope"),
 "v4pro":    (mla(61, 512, 64),             1048576, "61 layers of DSA latent attention, 512 + 64 rope"),
 "kimik3":   (mla(24, 512, 64),             1048576, "24 of 93 layers are full attention; the other 69 hold a fixed KDA state"),
 "qwenmax":  (gqa(23, 4, 256),              262144, "23 of 92 layers are full attention, one in every 4; the other 69 are linear"),
 # Generative media models have no growing KV cache to size, so there is no
 # per-token figure and the page hides the context table for them.
 "flux2k4":  (None, None, ""), "flux2k9": (None, None, ""),
 "zimage":   (None, None, ""), "ltx2":    (None, None, ""),
 "kokoro":   (None, None, ""), "magpie":  (None, None, ""),
 "voicechat":(None, None, ""), "mmmusic3":(None, None, ""),
 "qcnext":   (gqa(12, 2, 256),              262144, "12 of 48 layers are Gated Attention; the other 36 are Gated DeltaNet, which holds a fixed state"),
 "q38fnext": (gqa(12, 2, 256),              262144, "12 of 48 layers use Qwen Sparse Attention at micro-block granularity with a 2048 budget, so this is an upper bound; the other 36 are Gated DeltaNet"),
}

with open(OUT, "a") as f:
    f.write("\n# bytes of KV per token at fp16, the context ceiling, and how it was derived.\n")
    f.write("KV = " + pformat(KV) + "\n")

print("\nKV cost per token (fp16):")
for mid, (b, ctx, why) in KV.items():
    if b is None:
        print(f"  {mid:10s}      n/a   ctx {ctx:>9,}  {why}")
        continue
    print(f"  {mid:10s} {b/1024:7.1f} KiB  ctx {ctx:>9,}  "
          f"full ctx = {b*ctx/1e9:6.1f} GB   {why[:52]}")
