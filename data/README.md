# Data

| File | Content |
|---|---|
| `processed/ujjani_site_parameters.csv` | levels, storage zones, runoff statistics, fitted inflow parameters, demand split, with source of each |
| `processed/area_capacity_2017_18.csv` | CWC (2020) satellite-survey storage above MDDL vs water-spread area |
| `processed/monthly_inputs.csv` | demand and inflow weights, Solapur Tmax/Tmin, extraterrestrial radiation, Hargreaves ET0, open-water evaporation |
| `processed/synthetic_inflow_test_first10.csv` | first 10 of the 1,000 synthetic test sequences (MCM/month) |
| `raw/` | place for observed WRD / India-WRIS / CWC records when obtained |

Synthetic inflow: annual volume ~ lognormal, mean = k × 7,585 MCM (k = 0.40 reference), CV = 0.35 so that the 75 %-dependable/mean ratio equals CWC's 0.75; split over June–November with Dirichlet noise around shares 0.04, 0.22, 0.32, 0.26, 0.12, 0.03 (renormalised to sum to 1). Seeds are fixed in the code.

Units: 1 TMC = 28.3168 MCM; 1 cusec = 0.00244658 MCM/day.
