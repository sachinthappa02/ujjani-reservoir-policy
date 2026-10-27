# Optimising Release Policies for Ujjani Reservoir under Inflow Variability

## Ujjani (Yashwantrao Chavan Sagar), Bhima River, near Solapur, Maharashtra

**Student:** Sachin Thappa | **Roll:** 23B0709 
**Course:** CE 766  

---

## Overview

Ujjani Reservoir on the Bhima River supplies irrigation, drinking water for downstream towns and cities, and industrial demand. The basin is semi-arid and monsoon-driven, so inflow varies strongly from year to year. A fixed rule curve can cause shortages in dry years and spills in wet years.

This project investigates how Ujjani's release policy can be optimised to balance irrigation reliability, municipal supply security and storage resilience over 2000-2022, and how sensitive the trade-offs are to inflow variability. The approach follows the XLRM problem-framing idea and Evolutionary Multi-Objective Direct Policy Search (EMODPS): the release policy is a function of storage and month, and its parameters are optimised with a multi-objective evolutionary algorithm.

**Preliminary finding:** live storage (about 1,518 MCM) is only about 81% of planned annual utilisation (1,878 MCM). Stored water alone cannot carry supply through a dry year, so releases depend on in-season inflow and need to be hedged. This is a calculation from published storage figures, **not** a simulation result. The baseline simulation for 2000-2022 is pending the monthly data download (see [Status](#status)).

### Intended outcomes

1. A set of Pareto-optimal operating policies showing trade-offs between irrigation reliability, municipal supply reliability and spill/storage-risk objectives.
2. Quantified performance of the historical operation versus the optimised policies (reliability, resilience, vulnerability) in dry, normal and wet years.
3. Insight into how sensitive the best policies are to inflow uncertainty, including the conditions under which the reservoir fails to meet competing demands.

---

### Code

- `code/ujjani_baseline.py`: reconstructs monthly inflow (if no gauged series), runs a standard-operating-policy baseline, and computes reliability, resilience and vulnerability (Hashimoto et al., 1982) for all years and for dry, normal and wet water years. Python 3.8+.
- `code/make_figure1.py`: draws Figure 1 (storage zones against planned annual utilisation, and the model structure).

### Data

See [`data/README.md`](data/README.md) for the full data dictionary and download steps. The processed input is a monthly CSV with columns `date, storage_mcm, release_mcm, evap_mcm, inflow_mcm`. Only `date`, `storage_mcm` and `release_mcm` are required.

### Figures

- `figures/figure1_ujjani_storage_and_model.png`: Figure 1 used in the submission.

---

## Quick start

```
pip install -r requirements.txt

# smoke test on SYNTHETIC data (not Ujjani; only checks that the code runs)
python code/ujjani_baseline.py --demo

# real run, once data/processed/ujjani_monthly.csv exists
python code/ujjani_baseline.py data/processed/ujjani_monthly.csv

# redraw Figure 1
python code/make_figure1.py
```

Run all commands from the repository root. Outputs go to `results/` and `figures/`.

---

## Study site

| Parameter | Value |
|---|---|
| Location | Bhima River (Krishna basin tributary), near Solapur, Maharashtra |
| Gross storage | 3,320 MCM at FRL 497.58 m |
| Dead storage | about 1,802 MCM (54% of gross) |
| Live storage | about 1,518 MCM (gross minus dead) |
| Catchment area | 14,858 km² |
| Planned annual utilisation | 1,878 MCM (including evaporation) |
| Live storage / annual utilisation | about 81% (shortfall of about 360 MCM must come from inflow) |
| Same volumes as runoff depth over the catchment | utilisation about 126 mm, live storage about 102 mm |

Ujjani is unusual because its dead storage is larger than its live storage, so usable water depends strongly on the dead-storage boundary. Sources disagree on capacity: the figures above follow the Wikipedia entry for Ujjani Dam, while an online reservoir tracker lists 3,491 MCM gross. Whichever source is used must be stated in any result.

The catchment ranges from the high-rainfall Western Ghats to dry rain-shadow plains, and the Bhima is regulated by dams upstream of Ujjani, so reservoir inflow is not natural flow.

---

## Methodology

### Problem framing (XLRM)

| | Content |
|---|---|
| **X** (uncertainties) | inflow, demand, evaporation |
| **L** (levers) | release-policy parameters (release as a function of storage and month) |
| **R** (relationships) | monthly reservoir mass-balance model |
| **M** (metrics) | irrigation reliability, municipal reliability, vulnerability, spill risk |

### Model

A single lumped reservoir at a monthly time step. Monthly resolution matches how storage and release are reported, and the policy to be optimised varies with month and storage.

```
S(t+1) = S(t) + I(t) - R(t) - E(t) - Spill(t)

R(t)     <= max(0, S(t) + I(t) - E(t) - S_dead)      release only from water above dead storage
Spill(t)  = max(0, S(t) + I(t) - R(t) - E(t) - S_max)
S_dead = 1802 MCM,  S_max = 3320 MCM
```

- **S**: gross storage (MCM). **I**: net inflow. **R**: release to irrigation and municipal demand. **E**: evaporation (surface area times a Hargreaves-based depth; needs an area-capacity curve). **Spill**: water lost over the top.
- **Inflow reconstruction** (when no gauged inflow is available): `I(t) = S(t) - S(t-1) + R(t) + E(t)`.

### Baseline (no intervention)

Standard operating policy: release the demand whenever water above dead storage allows. Demand is 1,878 MCM/yr spread over months with weights set in `MONTH_W` in `code/ujjani_baseline.py`. The default is uniform and **must be replaced** with the real canal and municipal schedule.

Metrics follow Hashimoto et al. (1982): time-based reliability, resilience (probability of recovering from a failure month) and vulnerability (mean shortfall in failure months). Water years run June to May and are classed dry, normal or wet by inflow terciles.

### Planned next

Parameterise the policy (piecewise-linear hedging rule or radial basis functions, following Giuliani et al., 2016), optimise it with a multi-objective evolutionary algorithm (Borg or NSGA-II), generate synthetic inflow ensembles by bootstrap or a stochastic generator, evaluate robustness, and compare against historical operation with parallel-coordinates plots.

---

## Data sources

| Source | What it provides | Used for | Status |
|---|---|---|---|
| [India-WRIS](https://indiawris.gov.in/wris/) | reservoir storage and level time series | main source for 2000-2022 storage and release | to download |
| [National Water Data Portal: Ujjani Dam_1 gate discharge (hourly telemetry)](https://nwdp.nwic.gov.in/dataset/reservoir_discharge_ujjani_dam_1_maharashtra_telemetry_hourly) | hourly gate discharge in cusec | checking recent releases; the file reviewed begins in October 2023, so it does not cover the study period | reviewed |
| [CWC weekly reservoir level and storage bulletin](https://www.cwc.gov.in/reservoir-level-storage-bulletin) | weekly storage of major reservoirs | cross-checking storage, filling gaps | identified |
| [Global in-situ reservoir water-level dataset (GROWL), Scientific Data](https://www.nature.com/articles/s41597-026-07091-9) | compiled in-situ reservoir water levels and storage | candidate long series; coverage of Ujjani still to be checked | to check |
| [IMD](https://imdweb.lwcc.in/) | gridded rainfall and temperature | rainfall context; evaporation via Hargreaves | pending |
| [Wikipedia: Ujjani Dam](https://en.wikipedia.org/wiki/Ujjani_Dam) | storage zones, catchment, planned utilisation | model parameters | used |
| [reservoirs.earth: Bhima (Ujjani)](https://reservoirs.earth/india/reservoirs/bhima-ujjaini-in) | alternative capacity figures | shows the capacity discrepancy (3,491 vs 3,320 MCM gross) | noted |
| CAMELS-IND (search for the latest hosted version) | catchment hydrology, as listed in the course PDF | optional catchment context | optional |
| [Bhuvan](https://bhuvan.nrsc.gov.in/) | land cover | optional demand context | optional |
| [Copernicus Data Space](https://dataspace.copernicus.eu/), [USGS EarthExplorer](https://earthexplorer.usgs.gov/) | Sentinel-2 and Landsat imagery | optional water-extent validation | optional |

Conventions, unit conversions and the cleaning checklist are in [`data/README.md`](data/README.md).

---

## Preliminary results

![Figure 1](figures/figure1_ujjani_storage_and_model.png)

**Figure 1.** (a) Ujjani storage zones against planned annual utilisation; (b) structure of the monthly mass-balance model.

The 81% ratio in the figure is derived from the storage parameters above. Reliability, resilience and vulnerability from a real baseline run will be added to `results/` once the monthly series is cleaned.

---

## Status

- [x] Site parameters and storage-zone analysis
- [x] Model formulation and simulator code (tested on synthetic data only)
- [x] Data sources identified and reviewed
- [ ] Monthly storage and release for 2000-2022: downloading and cleaning in progress
- [ ] IMD temperature and evaporation
- [ ] Baseline run and validation
- [ ] Policy parameterisation and optimisation
- [ ] Inflow ensembles and robustness analysis

---

## Limitations

- Inflow is reconstructed from storage change and release, so storage validation against the same data is circular. An independent inflow record would fix this. Upstream regulation adds uncertainty.
- Monthly steps miss flood peaks and within-month operating decisions.
- Published capacity figures differ between sources (3,320 vs 3,491 MCM gross).
- The demand schedule in the baseline is an assumption until the real schedule is added.
- Evaporation needs an area-capacity curve that has not been sourced yet.
- Gate-discharge telemetry starts in October 2023, so it cannot validate 2000-2022.

---

## Next steps

1. Download and clean monthly storage and release for 2000-2022 into `data/processed/ujjani_monthly.csv`.
2. Replace the uniform demand weights with the real schedule, add evaporation, and run the baseline.
3. Parameterise the release policy and optimise it.
4. Generate inflow ensembles and compare optimised and historical operation by year type.

---

## References

Deb, K., Pratap, A., Agarwal, S., Meyarivan, T. (2002). A fast and elitist multiobjective genetic algorithm: NSGA-II. *IEEE Transactions on Evolutionary Computation*, 6(2), 182-197.

Giuliani, M., Castelletti, A., Pianosi, F., Mason, E., Reed, P. M. (2016). Curses, tradeoffs, and scalable management: advancing evolutionary multiobjective direct policy search to improve water reservoir operations. *Journal of Water Resources Planning and Management*, 142(2).

Hadka, D., Reed, P. (2013). Borg: an auto-adaptive many-objective evolutionary computing framework. *Evolutionary Computation*, 21(2), 231-259.

Hargreaves, G. H., Samani, Z. A. (1985). Reference crop evapotranspiration from temperature. *Applied Engineering in Agriculture*, 1(2), 96-99.

Hashimoto, T., Stedinger, J. R., Loucks, D. P. (1982). Reliability, resilience, and vulnerability criteria for water resource system performance evaluation. *Water Resources Research*, 18(1), 14-20.

# Data guide

Everything the code needs is one monthly CSV: `data/processed/ujjani_monthly.csv`. Original downloads go in `data/raw/` and are never edited by hand, so every number in the processed file can be traced back.

## Processed file format

| Column | Required | Unit | Meaning |
|---|---|---|---|
| `date` | yes | YYYY-MM-01 | first day of the month |
| `storage_mcm` | yes | MCM | **end-of-month gross storage** (dead + live) |
| `release_mcm` | yes | MCM | total outflow during that month (canal + river + spill) |
| `evap_mcm` | no | MCM | evaporation loss during that month (0 with a warning if missing) |
| `inflow_mcm` | no | MCM | gauged inflow during that month (if absent, inflow is reconstructed) |

`ujjani_monthly_TEMPLATE.csv` in `data/processed/` has the header only. Copy it to `ujjani_monthly.csv` and fill it.

## Where to get each series

| Series | Source | Notes |
|---|---|---|
| Storage / level (2000-2022) | [India-WRIS](https://indiawris.gov.in/wris/) reservoir section; or [GROWL](https://www.nature.com/articles/s41597-026-07091-9) if Ujjani is included | open the reservoir storage/level data, select Ujjani (Maharashtra), set the date range and export |
| Weekly storage cross-check | [CWC bulletin](https://www.cwc.gov.in/reservoir-level-storage-bulletin) | PDFs; useful for gap filling and spot checks |
| Gate discharge (recent only) | [NWDP Ujjani Dam_1](https://nwdp.nwic.gov.in/dataset/reservoir_discharge_ujjani_dam_1_maharashtra_telemetry_hourly) | hourly, in cusec; the file reviewed begins in October 2023 |
| Rainfall, temperature | [IMD](https://imdweb.lwcc.in/) | temperature drives Hargreaves evaporation |

## Unit conversions

- 1 TMC = 28.3168 MCM
- 1 cusec = 0.0283168 m³/s = 0.00244658 MCM/day
- Level (m) to storage needs the reservoir's elevation-capacity table. Record which table was used.

## Cleaning checklist

1. Convert everything to MCM and to end-of-month values (storage) or monthly totals (release, evaporation).
2. Check the water balance: months where reconstructed inflow comes out negative usually point to a data or unit problem.
3. Record gaps and how each was filled (interpolated, taken from the CWC bulletin, dropped).
4. State which capacity figure the storage series refers to (3,320 MCM or 3,491 MCM gross) and keep it consistent with `S_GROSS` and `S_DEAD` in `code/ujjani_baseline.py`.
5. Replace the uniform `MONTH_W` demand weights in the script with the real monthly demand schedule.

## Cleaning log

Lempert, R. J., Popper, S. W., Bankes, S. C. (2003). *Shaping the Next One Hundred Years: New Methods for Quantitative, Long-Term Policy Analysis*. RAND.
