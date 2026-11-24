# References

## Main references (cited in the report)
1. Giuliani, M., Castelletti, A., Pianosi, F., Mason, E. and Reed, P. M. (2016). Curses, tradeoffs, and scalable management: advancing evolutionary multiobjective direct policy search to improve water reservoir operations. *Journal of Water Resources Planning and Management*, 142(2), 04015050. https://doi.org/10.1061/(ASCE)WR.1943-5452.0000570
2. Hashimoto, T., Stedinger, J. R. and Loucks, D. P. (1982). Reliability, resiliency, and vulnerability criteria for water resource system performance evaluation. *Water Resources Research*, 18(1), 14–20. https://doi.org/10.1029/WR018i001p00014
3. Deb, K., Pratap, A., Agarwal, S. and Meyarivan, T. (2002). A fast and elitist multiobjective genetic algorithm: NSGA-II. *IEEE Transactions on Evolutionary Computation*, 6(2), 182–197. https://doi.org/10.1109/4235.996017

## Methods used in the code
- Hargreaves, G. H. and Samani, Z. A. (1985). Reference crop evapotranspiration from temperature. *Applied Engineering in Agriculture*, 1(2), 96–99. (evaporation)
- Allen, R. G., Pereira, L. S., Raes, D. and Smith, M. (1998). *Crop Evapotranspiration: Guidelines for Computing Crop Water Requirements*. FAO Irrigation and Drainage Paper 56. FAO, Rome. (extraterrestrial radiation, eq. 21)
- Blank, J. and Deb, K. (2020). pymoo: Multi-objective optimization in Python. *IEEE Access*, 8, 89497–89509. https://doi.org/10.1109/ACCESS.2020.2990567 (NSGA-II implementation)
- Kasprzyk, J. R., Nataraj, S., Reed, P. M. and Lempert, R. J. (2013). Many objective robust decision making for complex environmental systems undergoing change. *Environmental Modelling & Software*, 42, 55–71. (selecting the most robust Pareto policy)
- Bryant, B. P. and Lempert, R. J. (2010). Thinking inside the box: a participatory, computer-assisted approach to scenario discovery. *Technological Forecasting and Social Change*, 77(1), 34–49. (CART scenario discovery)
- Lempert, R. J., Popper, S. W. and Bankes, S. C. (2003). *Shaping the Next One Hundred Years: New Methods for Quantitative, Long-Term Policy Analysis*. RAND, Santa Monica. (XLRM framing)

## Datasets
- Central Water Commission (2020). *Sedimentation Assessment of Ujjani Reservoir, Maharashtra, through Satellite Remote Sensing.* Remote Sensing Directorate, CWC, New Delhi. https://cwc.gov.in/sites/default/files/sedimentation-assessment-ujjani-reservoir-through-srssep20.pdf  
  Used: FRL 496.83 m, MDDL 491.03 m, MWL 497.58 m; gross 3,320.01 MCM; dead 1,802.81 MCM; live 1,517.20 MCM (1977) and 1,347.07 MCM (2017–18); elevation–area–capacity tables; mean annual runoff 7,585 MCM; 75 % dependable runoff 5,688.75 MCM.
- India Meteorological Department, Sholapur station (43117): monthly temperature normals used for Hargreaves evaporation (values in `data/processed/monthly_inputs.csv`).

## Sources for behavioural checks and demand bounds
- Lokmat Times (10 May 2024). Solapur: water released from Ujani dam to alleviate severe shortage. (drinking-water release of 5.5 TMC through silt outlets; projected drawdown to −60 % live storage)
- The Bridge Chronicle (2024). Ujani Dam: swift rise in water level (storage zones in TMC; dam below live storage in July 2024).
- ThePrint / PTI (2025). Water released from Maharashtra's Ujani dam as its storage rises to 97 pc (dam normally fills by mid-August).
- Wikipedia, "Ujjani Dam" (planned annual utilisation 1.878 km³ and 2.410 km³ quoted in different versions; used for the demand-multiplier range 0.8–1.3).

## Sources reviewed in the proposal and preliminary submission (not used in final results)
- India-WRIS reservoir data: https://indiawris.gov.in/wris/
- National Water Data Portal, Ujjani Dam_1 gate discharge (hourly, from October 2023): https://nwdp.nwic.gov.in/dataset/reservoir_discharge_ujjani_dam_1_maharashtra_telemetry_hourly
- CWC weekly reservoir storage bulletin: https://www.cwc.gov.in/reservoir-level-storage-bulletin
- GROWL global in-situ reservoir water-level dataset (Scientific Data, 2026): https://doi.org/10.6084/m9.figshare.31225405
- Hadka, D. and Reed, P. (2013). Borg: an auto-adaptive many-objective evolutionary computing framework. *Evolutionary Computation*, 21(2), 231–259.
