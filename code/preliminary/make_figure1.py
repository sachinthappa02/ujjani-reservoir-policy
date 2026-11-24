"""Figure 1 for the Ujjani Data & Preliminary Results submission.
(a) storage zones vs planned annual utilisation, (b) mass-balance structure of the model.
All numbers: gross 3,320 MCM (FRL 497.58 m), dead 1,802 MCM, planned utilisation 1,878 MCM."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

GROSS, DEAD, DEMAND = 3320, 1802, 1878
LIVE = GROSS - DEAD
C_DEAD, C_LIVE, C_DEM, C_GAP, INK = "#9aa5b1", "#2f7fc1", "#e08a2e", "#f3c999", "#1f2933"

fig = plt.figure(figsize=(11.5, 5.2), dpi=200)
gs = fig.add_gridspec(1, 2, width_ratios=[1, 1.3], wspace=0.12)
a, b = fig.add_subplot(gs[0]), fig.add_subplot(gs[1])

# ---- (a) storage zones vs demand -------------------------------------------------
a.bar(0, DEAD, 0.62, color=C_DEAD, edgecolor="white")
a.bar(0, LIVE, 0.62, bottom=DEAD, color=C_LIVE, edgecolor="white")
a.bar(1, LIVE, 0.62, color=C_DEM, edgecolor="white")
a.bar(1, DEMAND - LIVE, 0.62, bottom=LIVE, color=C_GAP, edgecolor=C_DEM, hatch="//", lw=0.8)
a.axhline(GROSS, color=INK, ls=":", lw=0.9)
a.text(1.42, GROSS + 40, "Gross capacity 3,320 MCM (design, FRL 496.83 m)", ha="right", fontsize=8.5, color=INK)
a.text(0, DEAD / 2, f"Dead storage\n{DEAD:,} MCM\n(54% of gross)", ha="center", va="center", fontsize=9, color="white", weight="bold")
a.text(0, DEAD + LIVE / 2, f"Live storage\n{LIVE:,} MCM", ha="center", va="center", fontsize=9, color="white", weight="bold")
a.text(1, LIVE / 2, f"Live storage\ncovers {100*LIVE/DEMAND:.0f}%", ha="center", va="center", fontsize=9, color="white", weight="bold")
a.text(1, LIVE + (DEMAND - LIVE) / 2, f"{DEMAND-LIVE} MCM\nfrom inflow", ha="center", va="center", fontsize=8.5, color=INK)
a.text(1, DEMAND + 50, f"{DEMAND:,} MCM", ha="center", fontsize=9, color=INK, weight="bold")
a.set_xticks([0, 1]); a.set_xticklabels(["Reservoir storage\nzones", "Planned annual utilisation\n(incl. evaporation)"], fontsize=9)
a.set_ylabel("Volume (MCM)", fontsize=10); a.set_ylim(0, 3750); a.set_xlim(-0.55, 1.55)
for s in ("top", "right"): a.spines[s].set_visible(False)
a.set_title("(a) Storage zones vs annual planned use", loc="left", fontsize=10.5, weight="bold")

# ---- (b) model structure ---------------------------------------------------------
b.set_xlim(0, 11); b.set_ylim(0, 6.2); b.axis("off")
def box(x, y, w, h, txt, fc, ec, fs=9, tc=INK, bold=False):
    b.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.12", fc=fc, ec=ec, lw=1.2))
    b.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=fs, color=tc, weight="bold" if bold else "normal")
def arrow(x1, y1, x2, y2, c=INK):
    b.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=14, lw=1.4, color=c))

box(3.5, 2.1, 3.7, 2.0, "Ujjani reservoir\nS(t) \u2192 S(t+1)\nS_dead \u2264 S \u2264 S_max", "#dbeafe", C_LIVE, fs=9.5, bold=True)
box(0.0, 2.5, 2.7, 1.2, "Inflow I(t)\nmonsoon-driven,\nupstream-\nregulated", "#eef2f6", INK, fs=8.5)
arrow(2.75, 3.1, 3.45, 3.1)
box(8.0, 3.7, 3.0, 1.1, "Release R(t)\n(irrigation + municipal)", "#fdebd3", C_DEM, fs=8)
box(8.0, 2.55, 3.0, 0.85, "Evaporation E(t)", "#eef2f6", INK, fs=8.5)
box(8.0, 1.35, 3.0, 0.95, "Spill(t)\n(above S_max)", "#eef2f6", INK, fs=8.5)
arrow(7.25, 3.7, 7.95, 4.2); arrow(7.25, 3.0, 7.95, 2.97); arrow(7.25, 2.5, 7.95, 1.9)
box(3.1, 5.0, 4.5, 0.95, "Release policy R = f(S, month)\n(fixed rule curve vs optimised)", "#fdebd3", C_DEM, fs=8.5)
arrow(5.35, 4.95, 5.35, 4.15, C_DEM)
b.text(5.5, 0.55, "S(t+1) = S(t) + I(t) − R(t) − E(t) − Spill(t)", ha="center", fontsize=10.5, color=INK, family="monospace", weight="bold")
b.text(5.5, 0.12, "Monthly step · R limited to water above dead storage", ha="center", fontsize=8.5, color="#52606d")
b.set_title("(b) Monthly mass-balance model", loc="left", fontsize=10.5, weight="bold")

os.makedirs("figures", exist_ok=True)
fig.savefig("figures/figure1_ujjani_storage_and_model.png", bbox_inches="tight", facecolor="white")
