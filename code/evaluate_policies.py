"""
Re-evaluate SOP and the Pareto policies (1) on an independent test ensemble at the
reference scenario, by dry / normal / wet water year, and (2) across deeply uncertain
states of the world (Latin hypercube), with satisficing robustness and CART scenario discovery.
"""
import numpy as np
import pandas as pd
from scipy.stats import qmc
import ujjani_model as M

YEARS, K_REF = 23, 0.40
P = pd.read_csv("../results/pareto_policies.csv")
TH = P.filter(regex="^(alpha|u_lo|u_hi)_").values.reshape(-1, 12, 3)
SOP = np.tile([1.0, 0.0, 0.0], (12, 1))

# ---- compromise policy: closest to the ideal point in normalised objective space ----
F = P[["J1_neg_rel_irr", "J2_sqdef", "J3_p_dead"]].values
Fn = (F - F.min(0)) / (F.max(0) - F.min(0))
i_comp = int(np.argmin(np.sqrt((Fn ** 2).sum(1))))
COMP = TH[i_comp]

# ---- (1) test ensemble at the reference scenario ---------------------------------
N_TEST = 1000
Q, annual = M.synth_inflow(N_TEST, YEARS, K_REF, seed=2024)
lo, hi = np.quantile(annual, [1 / 3, 2 / 3])
ycls = np.where(annual <= lo, "dry", np.where(annual > hi, "wet", "normal"))   # (n, years)


def by_class(o):
    n = o["Dirr"].shape[0]
    D = o["Dirr"].reshape(n, YEARS, 12); R = o["Rirr"].reshape(n, YEARS, 12)
    S = o["S"].reshape(n, YEARS, 12)
    fail = R < D * (1 - 1e-6)
    rows = {}
    for c in ["dry", "normal", "wet"]:
        msk = ycls == c
        rows[c] = dict(rel_irr=1 - fail[msk].mean(),
                       supply_pct=100 * R[msk].sum() / D[msk].sum(),
                       worst_month_short=100 * ((D - R) / D)[msk].max(-1).mean(),
                       below_dead=(S[msk] < M.S_DEAD).mean())
    return pd.DataFrame(rows).T


rows, cls = [], []
for name, th in [("SOP (baseline)", None), ("Compromise hedging", COMP)]:
    o = M.simulate(Q, th)
    m = {k: v.mean() for k, v in M.measures(o).items()}
    m["evap"] = o["E"].sum(1).mean() / YEARS
    m["irr_supply_pct"] = 100 * o["Rirr"].sum() / o["Dirr"].sum()
    rows.append(dict(policy=name, **m))
    c = by_class(o); c["policy"] = name; cls.append(c)
    if th is not None:
        np.save("../results/comp_storage_sample.npy", o["S"][:5])
    else:
        np.save("../results/sop_storage_sample.npy", o["S"][:5])
test = pd.DataFrame(rows)
classes = pd.concat(cls).reset_index().rename(columns={"index": "year_class"})
test.to_csv("../results/test_ensemble_summary.csv", index=False)
classes.to_csv("../results/by_year_class.csv", index=False)
np.save("../results/inflow_sample.npy", Q[:5])

# all Pareto policies on the test ensemble (out-of-sample objectives)
oos = []
for th in TH:
    m = M.measures(M.simulate(Q, th))
    oos.append([m["rel_irr"].mean(), m["sq_def"].mean(), m["below_dead"].mean(), m["worst_year"].mean()])
P[["oos_rel_irr", "oos_sqdef", "oos_p_dead", "oos_worst_year"]] = np.array(oos)
m = M.measures(M.simulate(Q, None))
sop_oos = [m["rel_irr"].mean(), m["sq_def"].mean(), m["below_dead"].mean(), m["worst_year"].mean()]
P["is_compromise"] = False; P.loc[i_comp, "is_compromise"] = True
P.to_csv("../results/pareto_policies_evaluated.csv", index=False)
pd.DataFrame([sop_oos], columns=["oos_rel_irr", "oos_sqdef", "oos_p_dead", "oos_worst_year"]).to_csv(
    "../results/sop_oos.csv", index=False)

# ---- (2) deep uncertainty: Latin hypercube over X ---------------------------------
X_RANGES = {"k_reg": (0.25, 0.60), "cv": (0.25, 0.50), "demand_mult": (0.80, 1.30),
            "evap_mult": (0.80, 1.20), "rho": (0.0, 0.30)}
N_SOW, N_REAL = 400, 20
lhs = qmc.LatinHypercube(d=len(X_RANGES), seed=7).random(N_SOW)
lb, ub = np.array([v[0] for v in X_RANGES.values()]), np.array([v[1] for v in X_RANGES.values()])
sows = pd.DataFrame(qmc.scale(lhs, lb, ub), columns=list(X_RANGES))

# satisficing criteria (stakeholder thresholds; ASSUMPTION)
CRIT = dict(rel_mun=0.99, worst_year=0.50, below_dead=0.10)


def satisfies(m):
    return (m["rel_mun"] >= CRIT["rel_mun"]) & (m["worst_year"] <= CRIT["worst_year"]) & \
           (m["below_dead"] <= CRIT["below_dead"])


policies = {"SOP": None, **{f"P{i}": TH[i] for i in range(len(TH))}}
succ = {p: np.zeros(N_SOW) for p in policies}
all_m = {p: [] for p in policies}
for j, s in sows.iterrows():
    q, _ = M.synth_inflow(N_REAL, YEARS, s.k_reg, cv=s.cv, rho=s.rho, seed=1000 + j)
    for p, th in policies.items():
        m = M.measures(M.simulate(q, th, demand_mult=s.demand_mult, evap_mult=s.evap_mult))
        mm = {k: v.mean() for k, v in m.items()}
        succ[p][j] = satisfies(mm)
        all_m[p].append(mm)
rob = pd.Series({p: v.mean() for p, v in succ.items()})
P["robustness"] = rob[[f"P{i}" for i in range(len(TH))]].values
P.to_csv("../results/pareto_policies_evaluated.csv", index=False)
i_rob = int(P.robustness.values.argmax())          # SELECTED policy = most robust Pareto policy
P["is_selected"] = False; P.loc[i_rob, "is_selected"] = True
P.to_csv("../results/pareto_policies_evaluated.csv", index=False)
for tag, p in [("SOP", "SOP"), ("COMP", f"P{i_comp}"), ("SEL", f"P{i_rob}")]:
    sows[f"{tag}_success"] = succ[p].astype(bool)
    for k in ["rel_irr", "worst_year", "below_dead", "rel_mun", "sq_def"]:
        sows[f"{tag}_{k}"] = [d[k] for d in all_m[p]]
sows.to_csv("../results/states_of_world.csv", index=False)

# reference-scenario test tables for the selected policy
SEL = TH[i_rob]
o = M.simulate(Q, SEL)
m = {k: v.mean() for k, v in M.measures(o).items()}
m["evap"] = o["E"].sum(1).mean() / YEARS
m["irr_supply_pct"] = 100 * o["Rirr"].sum() / o["Dirr"].sum()
test = pd.concat([test, pd.DataFrame([dict(policy="Selected robust hedging", **m)])], ignore_index=True)
c = by_class(o); c["policy"] = "Selected robust hedging"
classes = pd.concat([classes, c.reset_index().rename(columns={"index": "year_class"})], ignore_index=True)
test.to_csv("../results/test_ensemble_summary.csv", index=False)
classes.to_csv("../results/by_year_class.csv", index=False)
np.save("../results/sel_storage_sample.npy", o["S"][:5])
pd.DataFrame(SEL, index=M.MONTHS, columns=["alpha", "u_lo", "u_hi"]).to_csv("../results/selected_policy_theta.csv")

print("compromise index", i_comp, "| most robust index", i_rob)
print(test.round(3).to_string(index=False))
print(classes.round(3).to_string(index=False))
print(f"Robustness: SOP {rob['SOP']:.3f} | compromise {rob[f'P{i_comp}']:.3f} | selected {rob[f'P{i_rob}']:.3f}")
print("Selected theta (alpha, u_lo, u_hi) by month:")
print(pd.DataFrame(SEL, index=M.MONTHS, columns=["alpha", "u_lo", "u_hi"]).round(2).T.to_string())
for tag in ["SOP", "SEL"]:
    print(tag, "criteria met: mun", (sows[f"{tag}_rel_mun"] >= CRIT["rel_mun"]).mean(),
          "| worst-year", (sows[f"{tag}_worst_year"] <= CRIT["worst_year"]).mean(),
          "| below-dead", (sows[f"{tag}_below_dead"] <= CRIT["below_dead"]).mean())

try:
    from sklearn.tree import DecisionTreeClassifier, export_text
    for col in ["SOP_success", "SEL_success"]:
        t = DecisionTreeClassifier(max_depth=2, min_samples_leaf=25, random_state=0).fit(
            sows[list(X_RANGES)], ~sows[col])
        print(f"\nCART failure rules, {col}:\n" + export_text(t, feature_names=list(X_RANGES)))
except ImportError:
    pass
