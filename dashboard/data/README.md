# Dashboard data

Anonymised aggregate results exported by the notebook: §15 writes most files and §12b writes the triage files. Sites appear only as codes (S01, S02, …); no place names, coordinates or chainage are included.

| File | Contents | Notebook section |
|---|---|---|
| `leakage_audit.csv` | Cross-validated F1, recall and AUC per domain for the leaky and fixed feature sets (XGBoost, identical folds) | §5 |
| `baselines.csv` | Cross-validated F1 and recall for the parameter-only, no-value-features and full models | §6 |
| `model_comparison.csv` | Nested time-series CV results (mean and SD) for three classifiers per domain, with holdout scores for each domain's winning model where a holdout exists | §7 |
| `smote_sensitivity.csv` | Change in F1 and recall when SMOTE is applied inside training folds | §8 |
| `ablation_rq3.csv` | Recall and F1 for spatial configurations A–D, with the D−A and C−B differences | §9 |
| `site_clusters.csv` | Exceedance rate per site and domain, zone type, cluster label and PCA coordinates | §10 |
| `site_priority.csv` | Mean predicted exceedance risk per site and domain, and the overall priority (risk only; the coverage and frequency gaps are not yet filled) | §13 |
| `timeseries_actual.csv` | Observed exceedance rate per month, zone and domain | §14 |
| `timeseries_predicted.csv` | Mean predicted risk per month, zone and domain | §14 |
| `exceedance_by_site_domain.csv` | Exceedance rate and number of readings per site and domain | §15 |
| `parameter_regimes.csv` | Exceedance rate, persistence and regime (chronic, episodic or compliant) per parameter | §12b |
| `zone_regime_effort.csv` | Share of readings in each regime, per zone | §12b |
| `zone_regime_burden.csv` | Share of exceedances in each regime, per zone | §12b |
| `zone_regime_misalignment.csv` | Effort share minus burden share, per zone and regime | §12b |

Zone types: `peri_urban`, `riverine`, `rural_agricultural`, `urban`. Domains: `air`, `surface_water`, `ground_water`, `noise`.
