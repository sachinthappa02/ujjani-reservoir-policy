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

Add one line per decision here (what was changed, why, which raw file).

- (empty)
