"""
EMODPS: optimise the monthly hedging rule (Q2 lever) with NSGA-II (pymoo).
Objectives (all minimised by pymoo):
  J1 = -Rel_irr        time-based irrigation reliability (Q1 measure)
  J2 = SqDef_irr       mean squared monthly irrigation deficit ratio (vulnerability)
  J3 = P_dead          fraction of months with storage below dead storage (storage risk)
Training ensemble: 100 synthetic 23-water-year inflow sequences (276 months).
"""
import time
import numpy as np
import pandas as pd
from pymoo.core.problem import Problem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
import ujjani_model as M

K_REF, YEARS, N_TRAIN = 0.40, 23, 100
Q_TRAIN, _ = M.synth_inflow(N_TRAIN, YEARS, K_REF, seed=11)


def objectives(theta_flat, Q=Q_TRAIN, **kw):
    m = M.measures(M.simulate(Q, theta_flat.reshape(12, 3), **kw))
    return np.array([-m["rel_irr"].mean(), m["sq_def"].mean(), m["below_dead"].mean()])


class Hedging(Problem):
    def __init__(self):
        super().__init__(n_var=36, n_obj=3, xl=np.zeros(36), xu=np.ones(36))

    def _evaluate(self, X, out, *a, **k):
        out["F"] = np.array([objectives(x) for x in X])


if __name__ == "__main__":
    t0 = time.time()
    rng = np.random.default_rng(1)
    X0 = rng.random((120, 36))
    X0[0] = np.tile([1.0, 0.0, 0.0], 12)          # seed the SOP (alpha = 1) so the front reaches it
    X0[1:10, 0::3] = rng.uniform(0.8, 1.0, (9, 12))
    res = minimize(Hedging(), NSGA2(pop_size=120, sampling=X0), ("n_gen", 250), seed=1, verbose=False)
    print(f"NSGA-II done in {time.time()-t0:.0f}s, {len(res.F)} non-dominated policies")
    sop = objectives(np.tile([1.0, 0.0, 0.0], 12))   # alpha=1 -> SOP
    print("SOP training objectives:", sop.round(4))
    cols = [f"{p}_{mo}" for mo in M.MONTHS for p in ("alpha", "u_lo", "u_hi")]
    df = pd.DataFrame(res.X, columns=cols)
    df["J1_neg_rel_irr"], df["J2_sqdef"], df["J3_p_dead"] = res.F.T
    df.to_csv("../results/pareto_policies.csv", index=False)
