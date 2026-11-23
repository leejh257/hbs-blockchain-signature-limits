"""Fig. 1: decomposition of signature size at a budget of 2^30 (policy V1, c = 2).

Sizes from Table 3: SLH-DSA-128s 7,856; S1 at 2^64 7,296; S1 at 2^30 4,528;
S3 4,396; S4 4,140; S5 3,900; S6 3,612; S7 3,276. S1 to S5 are reproduced by
costmodel/reproduce.py; S6 and S7 are not (see README, 'Not included').

Usage: python3 analysis/fig1.py   (writes fig1.png, fig1.svg and fig1.pdf to the current directory)
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["DejaVu Serif"],
    "mathtext.fontset": "dejavuserif",
    "font.size": 10.5,
    "svg.fonttype": "path",
})

GRAY, GREEN = "#8c8c8c", "#62a882"

steps = [
    ("SLH-DSA\n-128s", 7856, None),
    ("Re-\noptimize", 7296, None),
    ("Budget\nto 2³⁰", 4528, None),
    ("WOTS\n+C", 4396, None),
    ("FORS\n+C", 4140, None),
    ("PORS\n+FP", 3900, None),
    ("BPORS\n+FP", 3612, None),
    ("BPORS-C\n+BFP", 3276, None),
]
labels = [s[0] for s in steps] + ["Final\nset"]
sizes = [s[1] for s in steps]

fig, ax = plt.subplots(figsize=(6.6, 3.4))
W = 0.62
n = len(labels)

# start and end bars
ax.bar(0, sizes[0], W, color=GRAY)
ax.text(0, sizes[0] + 60, f"{sizes[0]:,}", ha="center", va="bottom")
ax.bar(n - 1, sizes[-1], W, color=GRAY)
ax.text(n - 1, sizes[-1] + 60, f"{sizes[-1]:,}", ha="center", va="bottom")

# reduction steps
for i in range(1, len(sizes)):
    top, bot = sizes[i - 1], sizes[i]
    ax.bar(i, top - bot, W, bottom=bot, color=GREEN)
    ax.text(i, top + 60, f"−{top - bot:,}", ha="center", va="bottom")

# connectors
for i in range(len(sizes)):
    ax.plot([i + W / 2, i + 1 - W / 2], [sizes[i]] * 2, ls="--", lw=0.8, color="#999999")

# bracket over the algorithmic variants (steps 3..7)
x0, x1, yb = 3 - W / 2, 7 + W / 2, 5300
ax.plot([x0, x0, x1, x1], [yb - 150, yb, yb, yb - 150], color="#555555", lw=1)
ax.text((x0 + x1) / 2, yb + 80, "variants together: −1,252 B", ha="center", va="bottom")

ax.set_xticks(range(n))
ax.set_xticklabels(labels, fontsize=9)
ax.set_ylabel("Signature size (bytes)")
ax.set_ylim(0, 8600)
ax.set_xlim(-0.6, n - 0.4)
ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
for s in ("top", "right"):
    ax.spines[s].set_visible(False)

fig.tight_layout()
fig.savefig("fig1.png", dpi=300)
fig.savefig("fig1.svg")
fig.savefig("fig1.pdf")
