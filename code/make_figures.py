"""Figure 1 (trade-offs + storage behaviour) and Figure 2 (robustness across uncertain futures)."""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import ujjani_model as M

INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
SOP_C, SEL_C = "#eb6834", "#2a78d6"            # categorical slots 2 and 1
SEQ = LinearSegmentedColormap.from_list("blue", ["#86b6ef", "#3987e5", "#256abf", "#104281", "#0d366b"])
plt.rcParams.update({"font.size": 10, "axes.edgecolor": INK2, "axes.labelcolor": INK,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False,
                     "axes.spines.right": False, "font.family": "DejaVu Sans"})
R = "../results/"
P = pd.read_csv(R + "pareto_policies_evaluated.csv")
sop = pd.read_csv(R + "sop_oos.csv").iloc[0]
sel = P[P.is_selected].iloc[0]

# ---------------------------------- Figure 1 ----------------------------------------
fig, ax = plt.subplots(1, 2, figsize=(12, 4.9), gridspec_kw=dict(width_ratios=[1.05, 1], wspace=0.28))
a = ax[0]
sc = a.scatter(100 * P.oos_rel_irr, P.oos_sqdef, c=100 * P.oos_p_dead, cmap=SEQ, s=34,
               edgecolor="white", lw=0.8, vmin=0, vmax=13, zorder=3)
a.scatter(100 * sop.oos_rel_irr, sop.oos_sqdef, marker="*", s=320, color=SOP_C, edgecolor="white", lw=1, zorder=5)
a.annotate(f"Baseline SOP\n{100*sop.oos_p_dead:.1f}% of months below dead storage",
           (100 * sop.oos_rel_irr, sop.oos_sqdef), xytext=(21, 0.192), fontsize=9, color=INK,
           arrowprops=dict(arrowstyle="-", color=INK2, lw=0.8))
a.scatter(100 * sel.oos_rel_irr, sel.oos_sqdef, s=190, facecolor="none", edgecolor=INK, lw=1.8, zorder=6)
a.annotate(f"Selected robust policy\n{100*sel.oos_p_dead:.1f}% of months below dead storage",
           (100 * sel.oos_rel_irr, sel.oos_sqdef), xytext=(21, 0.150), fontsize=9, color=INK,
           arrowprops=dict(arrowstyle="-", color=INK2, lw=0.8))
a.annotate("Better", xy=(85, 0.063), xytext=(80.5, 0.076), fontsize=9, color=INK2, ha="center",
           arrowprops=dict(arrowstyle="-|>", color=INK2, lw=1))
cb = fig.colorbar(sc, ax=a, pad=0.02, fraction=0.05)
cb.set_label("Months with storage below dead storage (%)", color=INK)
cb.outline.set_visible(False)
a.set_xlabel("Irrigation reliability, Rel_irr (% of months with full demand met)")
a.set_ylabel("Irrigation vulnerability\n(mean squared monthly deficit ratio, lower = better)")
a.set_xlim(20, 86); a.set_ylim(0.06, 0.2)
a.grid(color=GRID, lw=0.6); a.set_axisbelow(True)
a.set_title("(a) Trade-offs among 120 optimised hedging policies", loc="left", fontsize=11, weight="bold")

b = ax[1]
x = np.arange(12)
for name, f, c in [("Baseline SOP", "sop_storage_sample", SOP_C), ("Selected robust policy", "sel_storage_sample", SEL_C)]:
    pass
# full ensemble storage percentiles by calendar month
Q, _ = M.synth_inflow(1000, 23, 0.40, seed=2024)
theta_sel = pd.read_csv(R + "selected_policy_theta.csv", index_col=0).values
for name, th, c in [("Baseline SOP", None, SOP_C), ("Selected robust policy", theta_sel, SEL_C)]:
    S = M.simulate(Q, th)["S"].reshape(1000, 23, 12)[:, 1:, :].reshape(-1, 12)
    p10, p50, p90 = np.percentile(S, [10, 50, 90], axis=0)
    b.fill_between(x, p10, p90, color=c, alpha=0.16, lw=0)
    b.plot(x, p50, color=c, lw=2, marker="o", ms=4, label=f"{name} (median, 10–90% band)")
b.axhline(M.S_DEAD, color=INK, ls="--", lw=1)
b.text(11.2, M.S_DEAD + 25, "Dead storage 1,803 MCM", ha="right", fontsize=9, color=INK)
b.axhline(M.S_MAX, color=INK2, ls=":", lw=1)
b.text(11.2, M.S_MAX + 25, "FRL capacity after silting 3,150 MCM", ha="right", fontsize=9, color=INK2)
b.set_xticks(x); b.set_xticklabels(M.MONTHS)
b.set_ylabel("End-of-month gross storage (MCM)")
b.set_xlabel("Month of water year (June–May)")
b.set_ylim(1100, 3350)
b.legend(loc="lower left", fontsize=8.5, frameon=False)
b.grid(axis="y", color=GRID, lw=0.6); b.set_axisbelow(True)
b.set_title("(b) Storage through the water year", loc="left", fontsize=11, weight="bold")
fig.savefig("../figures/Figure1_tradeoffs_and_storage.png", dpi=200, bbox_inches="tight", facecolor="white")

# ---------------------------------- Figure 2 ----------------------------------------
W = pd.read_csv(R + "states_of_world.csv")
fig, ax = plt.subplots(1, 2, figsize=(12, 4.8), sharey=True, gridspec_kw=dict(wspace=0.08))
for a, tag, title, c in [(ax[0], "SOP", "(a) Baseline SOP", SEL_C), (ax[1], "SEL", "(b) Selected robust hedging policy", SEL_C)]:
    ok = W[f"{tag}_success"]
    xin, yd = W.k_reg * M.MEAN_RUNOFF, W.demand_mult * M.DEMAND_TOTAL
    a.scatter(xin[~ok], yd[~ok], s=26, facecolor="white", edgecolor="#9a9994", lw=0.9, label="Fails ≥1 criterion")
    a.scatter(xin[ok], yd[ok], s=30, color=c, edgecolor="white", lw=0.6, label="Meets all criteria")
    a.scatter(0.40 * M.MEAN_RUNOFF, M.DEMAND_TOTAL, marker="X", s=150, color=INK, edgecolor="white", lw=1, zorder=5,
              label="Reference scenario")
    a.set_title(f"{title}: robust in {100*ok.mean():.1f}% of 400 futures", loc="left", fontsize=11, weight="bold")
    a.set_xlabel("Mean annual inflow to Ujjani (MCM/yr)")
    a.grid(color=GRID, lw=0.6); a.set_axisbelow(True)
ax[0].set_ylabel("Annual release demand (MCM/yr)")
h, l = ax[1].get_legend_handles_labels()
fig.legend(h, l, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.07), frameon=False, fontsize=9.5)
fig.text(0.5, -0.12, "Criteria: drinking-water reliability ≥ 99%;  worst water-year irrigation shortfall ≤ 50%;  "
         "storage below dead storage in ≤ 10% of months.  Each point = one future (mean of 20 × 23-year sequences).",
         ha="center", fontsize=9, color=INK2)
fig.savefig("../figures/Figure2_robustness_map.png", dpi=200, bbox_inches="tight", facecolor="white")
print("figures written")
