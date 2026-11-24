"""
Ujjani Reservoir (Bhima River, Maharashtra): monthly mass-balance model,
synthetic-inflow generator, evaporation and performance measures.

Every site parameter below is taken from the CWC (2020) sedimentation assessment
of Ujjani unless marked ASSUMPTION.
Vectorised over realisations: arrays have shape (n_realisations, n_months).
"""
import numpy as np
from scipy.stats import norm
from scipy.optimize import brentq

# ---------------- site parameters (CWC 2020) ----------------------------------
S_DEAD = 1802.81            # MCM, dead storage at MDDL 491.03 m
LIVE_1977 = 1517.20         # MCM, original live storage
LIVE_2018 = 1347.07         # MCM, live storage from 2017-18 satellite survey
S_MAX = S_DEAD + LIVE_2018  # MCM, storage at FRL 496.83 m after sedimentation (3149.9)
MEAN_RUNOFF = 7585.0        # MCM/yr, average annual runoff at dam site
DEP75_RUNOFF = 5688.75      # MCM/yr, 75 % dependable runoff
# 2017-18 SRS elevation-area-capacity table (live zone): storage above MDDL vs area
CAP_LIVE = np.array([0.0, 185.141, 393.357, 618.820, 861.152, 1119.977, 1347.074])
AREA = np.array([182.300, 199.564, 216.991, 234.042, 250.718, 267.017, 280.260])  # Mm2 (=km2)

# emergency floor for drinking-water releases from silt blocks (2024 drawdown to about -60 % live)
S_EMERG = S_DEAD - 0.60 * LIVE_2018          # ~994 MCM

# ---------------- demand (ASSUMPTION, documented in README) -------------------
DEMAND_TOTAL = 1878.0                        # MCM/yr planned utilisation
D_MUN_ANNUAL = 283.0                         # MCM/yr = 10 TMC drinking + industrial
D_IRR_ANNUAL = DEMAND_TOTAL - D_MUN_ANNUAL   # 1595 MCM/yr
# water-year order Jun..May; rabi + hot-weather (sugarcane) dominated canal schedule
IRR_W = np.array([0.05, 0.03, 0.03, 0.04, 0.08, 0.10, 0.12, 0.10, 0.10, 0.11, 0.12, 0.12])
MUN_W = np.full(12, 1 / 12)
# monthly share of annual inflow, Jun..May (monsoon-driven; ASSUMPTION)
INFLOW_W = np.array([0.04, 0.22, 0.32, 0.26, 0.12, 0.03, 0.01, 0, 0, 0, 0, 0])
MONTHS = ["Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May"]

# ---------------- evaporation: Hargreaves-Samani (1985) -------------------------
# Solapur climatological normals, Jun..May (Tmax, Tmin in degC)
TMAX = np.array([34.0, 30.6, 29.9, 30.9, 31.6, 30.6, 30.1, 31.5, 34.3, 37.7, 40.0, 39.6])
TMIN = np.array([23.6, 22.6, 22.0, 21.6, 20.6, 17.9, 15.8, 16.3, 18.5, 21.9, 24.8, 25.3])
LAT = np.deg2rad(18.07)
DAYS = np.array([30, 31, 31, 30, 31, 30, 31, 31, 28.25, 31, 30, 31])
MID_DOY = np.array([166, 196, 227, 258, 288, 319, 349, 15, 46, 74, 105, 135])
K_OPEN_WATER = 1.10   # open-water / reference ET (ASSUMPTION; pan-coefficient-type factor)


def extraterrestrial_radiation_mm(doy):
    """FAO-56 eq. 21, returned as equivalent evaporation (mm/day)."""
    dr = 1 + 0.033 * np.cos(2 * np.pi * doy / 365)
    dec = 0.409 * np.sin(2 * np.pi * doy / 365 - 1.39)
    ws = np.arccos(-np.tan(LAT) * np.tan(dec))
    ra = 24 * 60 / np.pi * 0.0820 * dr * (ws * np.sin(LAT) * np.sin(dec) + np.cos(LAT) * np.cos(dec) * np.sin(ws))
    return 0.408 * ra


RA = extraterrestrial_radiation_mm(MID_DOY)
ET0_DAY = 0.0023 * RA * ((TMAX + TMIN) / 2 + 17.8) * np.sqrt(TMAX - TMIN)
EVAP_M = K_OPEN_WATER * ET0_DAY * DAYS / 1000.0   # m/month, Jun..May


def area_km2(S):
    """Water-spread area from storage: CWC 2017-18 table above MDDL, power law below."""
    live = S - S_DEAD
    a_up = np.interp(live, CAP_LIVE, AREA)
    a_low = AREA[0] * np.clip(S / S_DEAD, 0, None) ** (2 / 3)
    return np.where(live >= 0, a_up, a_low)


# ---------------- synthetic inflow ----------------------------------------------
def lognormal_params(mean, q25):
    """sigma such that the 25th percentile / mean ratio of a lognormal equals q25/mean."""
    r = q25 / mean
    sig = brentq(lambda s: np.exp(-s ** 2 / 2 + norm.ppf(0.25) * s) - r, 1e-3, 3)
    return np.log(mean) - sig ** 2 / 2, sig


MU0, SIG0 = lognormal_params(MEAN_RUNOFF, DEP75_RUNOFF)
CV0 = float(np.sqrt(np.exp(SIG0 ** 2) - 1))


def synth_inflow(n, years, k_reg, cv=None, rho=0.0, seed=0):
    """Monthly inflow (n, years*12), MCM. Annual lognormal (mean = k_reg * CWC mean),
    lag-1 correlation rho, monthly split with Dirichlet noise around INFLOW_W."""
    rng = np.random.default_rng(seed)
    cv = CV0 if cv is None else cv
    sig = np.sqrt(np.log(1 + cv ** 2))
    mu = np.log(k_reg * MEAN_RUNOFF) - sig ** 2 / 2
    z = rng.standard_normal((n, years))
    for y in range(1, years):
        z[:, y] = rho * z[:, y - 1] + np.sqrt(1 - rho ** 2) * z[:, y]
    annual = np.exp(mu + sig * z)
    w = INFLOW_W[:6]
    shares = rng.dirichlet(w * 60, size=(n, years))       # monsoon months only
    q = np.zeros((n, years, 12))
    q[:, :, :6] = annual[:, :, None] * shares
    return q.reshape(n, years * 12), annual


# ---------------- simulation ------------------------------------------------------
def simulate(inflow, theta=None, demand_mult=1.0, evap_mult=1.0, s0=None):
    """
    inflow: (n, T) MCM/month, T a multiple of 12, month 0 = June.
    theta: None -> standard operating policy (SOP); else array (12, 3) of
           [alpha, u_lo, u_hi] per month:  S_lo = S_DEAD + u_lo*LIVE,
           S_hi = S_lo + u_hi*(S_MAX - S_lo).
    Returns dict of arrays (n, T).
    """
    n, T = inflow.shape
    S = np.full(n, S_DEAD + 0.5 * LIVE_2018) if s0 is None else np.full(n, s0)
    out = {k: np.zeros((n, T)) for k in ["S", "Rirr", "Rmun", "Dirr", "Dmun", "E", "Spill", "f"]}
    for t in range(T):
        m = t % 12
        d_irr = demand_mult * D_IRR_ANNUAL * IRR_W[m]
        d_mun = demand_mult * D_MUN_ANNUAL * MUN_W[m]
        E = evap_mult * EVAP_M[m] * area_km2(S)              # km2 * m = MCM
        W = S + inflow[:, t] - E
        # municipal first; may draw below dead storage down to the emergency floor
        r_mun = np.minimum(d_mun, np.maximum(0.0, W - S_EMERG))
        A_irr = np.maximum(0.0, W - r_mun - S_DEAD)          # irrigation only above dead storage
        if theta is None:
            f = np.ones(n)
        else:
            a, ulo, uhi = theta[m]
            s_lo = S_DEAD + ulo * LIVE_2018
            s_hi = s_lo + uhi * (S_MAX - s_lo)
            f = np.clip(a + (1 - a) * (S - s_lo) / max(s_hi - s_lo, 1e-6), a, 1.0)
        r_irr = np.minimum(f * d_irr, A_irr)
        S_new = W - r_mun - r_irr
        spill = np.maximum(0.0, S_new - S_MAX)
        S_new = S_new - spill
        for k, v in zip(["Rirr", "Rmun", "E", "Spill", "f"], [r_irr, r_mun, E, spill, f]):
            out[k][:, t] = v
        out["Dirr"][:, t] = d_irr
        out["Dmun"][:, t] = d_mun
        S = S_new
        out["S"][:, t] = S
    return out


def measures(o, tol=1e-6):
    """Per-realisation measures (arrays of length n)."""
    Dirr, Rirr, Dmun, Rmun = o["Dirr"], o["Rirr"], o["Dmun"], o["Rmun"]
    fail = Rirr < Dirr * (1 - tol)                         # Q1: d(t)=0
    rel_irr = 1 - fail.mean(1)
    defr = np.where(Dirr > 0, (Dirr - Rirr) / Dirr, 0)
    sq_def = (defr ** 2).mean(1)                           # mean squared deficit ratio
    nf = fail.sum(1)
    vul = np.where(nf > 0, (defr * fail).sum(1) / np.maximum(nf, 1), 0.0)
    res = np.where(nf > 0, (fail[:, :-1] & ~fail[:, 1:]).sum(1) / np.maximum(nf, 1), 1.0)
    rel_mun = 1 - (Rmun < Dmun * (1 - tol)).mean(1)
    n, T = Dirr.shape
    yr_supply = Rirr.reshape(n, T // 12, 12).sum(2) / Dirr.reshape(n, T // 12, 12).sum(2)
    worst_year = 1 - yr_supply.min(1)                     # worst water-year irrigation shortfall
    spill = o["Spill"].sum(1) / (T / 12)
    below_dead = (o["S"] < S_DEAD).mean(1)
    return dict(rel_irr=rel_irr, sq_def=sq_def, vul=vul, res=res, rel_mun=rel_mun,
                worst_year=worst_year, spill=spill, below_dead=below_dead)
