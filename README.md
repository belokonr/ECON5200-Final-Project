# ECON5200-Final-Project

# Does Remote Work Reduce Housing Prices?

**A Causal Analysis Using Double Machine Learning**

ECON 5200 — Consulting Report Final Project

---

## Overview

This project investigates whether the rise in remote work adoption *causes* changes in state-level housing prices across the United States. Using Double Machine Learning (DML), we separate the true causal effect of work-from-home (WFH) rates on the FHFA House Price Index from the confounding influence of state economic conditions.

## Key Findings

**The naive estimate is misleading.** A simple OLS regression of housing prices on WFH rates produces a coefficient of **+1,923.6**, suggesting remote work is associated with *higher* housing prices. This is driven by omitted variable bias — wealthy, tech-heavy states like California and Massachusetts have both high WFH rates and expensive housing.

**DML reveals a dramatically different picture.** After using Gradient Boosting models to partial out confounding from unemployment, per-capita income, and population, the causal estimate drops to **673.0** (95% CI: [344.0, 1,002.0]) — a **65% reduction** from the naive estimate. The 1,250-point difference is entirely attributable to omitted variable bias.

**The result is robust.** Three different first-stage ML specifications all produce positive, statistically significant estimates with overlapping confidence intervals:

| Method | ATE | 95% CI |
|--------|-----|--------|
| DML (Gradient Boosting) | 673.0 | [344.0, 1,002.0] |
| DML (Random Forest) | 898.2 | [524.1, 1,272.3] |
| DML (Lasso) | 799.4 | [444.7, 1,154.0] |

**Prediction ≠ Causation.** A Random Forest predictive model achieves R² = 0.493, and ranks WFH rate as the second most important feature (importance = 0.197). But this importance score conflates the causal channel with confounded correlation — it cannot tell a policymaker what would happen if WFH rates changed. Only the DML estimate answers that question.

## Data

The analysis uses a panel of **51 states × 5 years** (2018, 2019, 2021–2023). The 2020 ACS 1-year was not released due to COVID data collection disruptions.

| Variable | Source |
|----------|--------|
| WFH Rate | Census ACS 1-Year (Table B08301) |
| House Price Index | FHFA All-Transactions HPI (via FRED) |
| Unemployment Rate | BLS LAUS (via FRED) |
| Per-Capita Income | BEA (via FRED) |
| Population | Census ACS 1-Year |

## Repository Contents

```
├── 5200_final_project_notebook.ipynb   # Complete notebook with all results and models
├── 5200_final_project_starter.ipynb    # Starter notebook with EDA only
├── app.py                              # Streamlit dashboard for interactive what-if analysis
├── requirements.txt                    # Python dependencies for the Streamlit app
└── README.md
```

## How to Run

### Jupyter Notebook

1. Open `5200_final_project_notebook.ipynb` in Google Colab or Jupyter.
2. Obtain free API keys from [FRED](https://fred.stlouisfed.org/docs/api/api_key.html) and [Census](https://api.census.gov/data/key_signup.html).
3. Replace `YOUR_FRED_API_KEY_HERE` and `YOUR_CENSUS_API_KEY_HERE` in the data loading cell.
4. Run all cells sequentially. The notebook will pull live data from the FRED and Census APIs, run the EDA, fit the naive OLS, DML causal model, predictive model, and robustness checks.

**Note:** The `econml` package is required for DML. The first cell installs it via `!pip install econml`.

### Streamlit Dashboard

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the app locally:
   ```bash
   streamlit run app.py
   ```
3. The dashboard opens at `http://localhost:8501`. Use the sidebar controls to explore what-if scenarios for different WFH rate increases and confidence levels.

### Deploying to Streamlit Community Cloud

1. Push this repository to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **New app**, select this repo, set the main file to `app.py`, and deploy.

## Methodology

The project uses **Double Machine Learning** (Chernozhukov et al., 2018) implemented via the [EconML](https://github.com/py-why/EconML) library. DML works in two stages:

1. **First stage:** Train ML models to predict both the outcome (HPI) and the treatment (WFH rate) from confounders using 5-fold cross-fitting. This removes the predictable, confounded variation.
2. **Second stage:** Regress the residualized outcome on the residualized treatment to estimate the average treatment effect (ATE).

This approach allows flexible, nonlinear modeling of confounders while still providing valid confidence intervals for the causal parameter.

## Limitations

- **Missing 2020 data** removes the peak WFH shock year from the analysis.
- **Unobserved industry composition** (tech/finance sector concentration) may still confound the estimate beyond what per-capita income captures.
- **Residential proxy:** The FHFA HPI covers residential real estate, not the commercial market that is the ultimate target of the research question.
- **Reverse causality** cannot be fully ruled out — expensive housing may itself incentivize remote work adoption.

## AI Acknowledgement

The notebooks, conception, and feedback for this project were developed with the assistance of Claude (Anthropic, claude.ai). Claude was used as a collaborative coding and writing tool to design the interaction model specifications, implement the methods for subgroup effect estimation, generate the Streamlit dashboard, and draft documentation. All analytical decisions and interpretations were reviewed and directed by the project author.
