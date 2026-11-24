"""
Ujjani Reservoir - baseline (no-intervention) monthly simulation.

Usage (run from the repository root)
    python code/ujjani_baseline.py data/processed/ujjani_monthly.csv
    python code/ujjani_baseline.py --demo   # SYNTHETIC data, only to test the pipeline

Input CSV columns (monthly, one row per month, MCM = million m3):
    date          first day of month, e.g. 2005-06-01
    storage_mcm   END-of-month GROSS storage (dead + live)
    release_mcm   total outflow in that month (canal + river + spill)
  optional:
    evap_mcm      evaporation loss in that month (if missing it is set to 0 with a warning)
    inflow_mcm    observed/gauged inflow (if present it is used instead of reconstruction)

Outputs: results/baseline_monthly.csv, results/baseline_summary.csv, figures/baseline_figure.png
(prefixed DEMO_ when --demo is used, so they cannot be mistaken for real results)
"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---- site parameters: check against the source you cite ----------------------
S_GROSS = 3320.0                 # MCM at FRL 497.58 m
S_DEAD = 1802.0                  # MCM (about 63.65 TMC)
DEMAND_ANNUAL = 1878.0           # MCM, planned annual utilisation incl. evaporation
MONTH_W = np.full(12, 1 / 12)    # Jan..Dec weights; REPLACE with the canal/municipal schedule
# -------------------------------------------------------------------------------


def load(path):
    df = pd.read_csv(path, parse_dates=["date"]).sort_values("date").reset_index(drop=True)
    missing = {"date", "storage_mcm", "release_mcm"} - set(df.columns)
    if missing:
        raise ValueError(f"missing columns: {missing}")
    if "evap_mcm" not in df:
        print("WARNING: no evap_mcm column - evaporation set to 0")
        df["evap_mcm"] = 0.0
    if "inflow_mcm" not in df:
        # I(t) = S(t) - S(t-1) + R(t) + E(t)   (reconstructed net inflow)
        df["inflow_mcm"] = df.storage_mcm.diff() + df.release_mcm + df.evap_mcm
        df["inflow_source"] = "reconstructed"
    else:
        df["inflow_source"] = "observed"
    neg = (df.inflow_mcm < 0).sum()
    if neg:
        print(f"WARNING: {neg} months with negative inflow - clipped to 0 (check data)")
    df["inflow_mcm"] = df.inflow_mcm.clip(lower=0)
    s0 = df.storage_mcm.iloc[0]  # opening storage for the first simulated month
    out = df.iloc[1:].reset_index(drop=True)  # first month has no storage change
    out.attrs["s0"] = s0
    return out


def simulate(inflow, evap, demand, s0):
    """Standard operating policy: release the demand if water above dead storage allows."""
    n = len(inflow)
    S, R, SP = np.zeros(n), np.zeros(n), np.zeros(n)
    s = s0
    for t in range(n):
        avail = s + inflow[t] - evap[t]
        r = min(demand[t], max(0.0, avail - S_DEAD))
        sp = max(0.0, avail - r - S_GROSS)
        s = avail - r - sp
        S[t], R[t], SP[t] = s, r, sp
    return S, R, SP


def metrics(D, R, tol=1e-3):
    """Hashimoto et al. (1982): time-based reliability, resilience, vulnerability."""
    fail = R < D * (1 - tol)
    nf = fail.sum()
    rel = 1 - fail.mean()
    res = ((fail[:-1] & ~fail[1:]).sum() / nf) if nf else np.nan   # nan = never failed
    vul = ((D - R)[fail] / D[fail]).mean() if nf else 0.0
    return dict(months=len(D), failures=int(nf), reliability=rel, resilience=res, vulnerability=vul)


def water_year(d):  # June-May
    return d.dt.year.where(d.dt.month >= 6, d.dt.year - 1)


def demo_data():
    rng = np.random.default_rng(0)
    dates = pd.date_range("2000-06-01", "2022-05-01", freq="MS")
    seas = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.1, 0.45, 0.3, 0.1, 0.03, 0.02])  # Jan..Dec
    yr = rng.gamma(2.5, 1100.0, size=len(dates) // 12 + 1)
    inflow = np.array([yr[i // 12] * seas[d.month - 1] * rng.uniform(0.6, 1.4) for i, d in enumerate(dates)])
    D = DEMAND_ANNUAL * MONTH_W[dates.month - 1]
    S, R, _ = simulate(inflow, np.zeros(len(dates)), D, S_DEAD + 600)
    return pd.DataFrame({"date": dates, "storage_mcm": S, "release_mcm": R})


def main(path, prefix=""):
    os.makedirs("results", exist_ok=True)
    os.makedirs("figures", exist_ok=True)
    df = load(path)
    D = DEMAND_ANNUAL * MONTH_W[df.date.dt.month.values - 1]
    S0 = df.attrs["s0"]
    S, R, SP = simulate(df.inflow_mcm.values, df.evap_mcm.values, D, S0)
    df = df.assign(demand_mcm=D, sim_storage_mcm=S, sim_release_mcm=R, sim_spill_mcm=SP)

    # dry / normal / wet water years by inflow terciles
    df["wy"] = water_year(df.date)
    wy_in = df.groupby("wy").inflow_mcm.sum()
    lo, hi = wy_in.quantile([1 / 3, 2 / 3])
    cls = wy_in.map(lambda x: "dry" if x <= lo else ("wet" if x > hi else "normal"))
    df["year_class"] = df.wy.map(cls)

    rows = [dict(group="all", **metrics(D, R))]
    for c in ["dry", "normal", "wet"]:
        m = (df.year_class == c).values
        rows.append(dict(group=c, **metrics(D[m], R[m])))
    summ = pd.DataFrame(rows)
    summ["total_spill_mcm"] = [SP.sum()] + [SP[(df.year_class == c).values].sum() for c in ["dry", "normal", "wet"]]

    print(summ.round(3).to_string(index=False))
    print("\nwater-year inflow terciles (MCM): dry <=", round(lo), "| wet >", round(hi))
    df.to_csv(f"results/{prefix}baseline_monthly.csv", index=False)
    summ.to_csv(f"results/{prefix}baseline_summary.csv", index=False)

    fig, ax = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
    ax[0].plot(df.date, df.storage_mcm, label="observed storage", lw=1.2)
    ax[0].plot(df.date, df.sim_storage_mcm, label="simulated (baseline)", lw=1, ls="--")
    ax[0].axhline(S_DEAD, color="k", lw=0.8, ls=":", label="dead storage")
    ax[0].axhline(S_GROSS, color="grey", lw=0.8, ls=":", label="gross capacity")
    ax[0].set_ylabel("Storage (MCM)"); ax[0].legend(ncol=2, fontsize=8)
    ax[1].bar(df.date, df.demand_mcm - df.sim_release_mcm, width=25, color="tab:red")
    ax[1].set_ylabel("Unmet demand (MCM)")
    fig.suptitle(f"{prefix}Ujjani baseline simulation, standard operating policy")
    fig.tight_layout(); fig.savefig(f"figures/{prefix}baseline_figure.png", dpi=200)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        os.makedirs("results", exist_ok=True)
        demo_data().to_csv("results/DEMO_input.csv", index=False)
        main("results/DEMO_input.csv", prefix="DEMO_")
    elif len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print(__doc__)
