# Credit Risk & IFRS 9 Expected Credit Loss (ECL) Model

An end-to-end retail credit risk pipeline that mirrors how UK banks and building societies model
**Probability of Default (PD)**, assign **IFRS 9 stages** (Stage 1 / 2 / 3), and calculate
**Expected Credit Loss (ECL)** — including a macroeconomic stress overlay — to meet IFRS 9
impairment and PRA stress-testing requirements.

> Built by Sahil Singh Choudhary as a portfolio project demonstrating practical application of
> credit risk modelling, IFRS 9 methodology, and Basel-aligned regulatory reporting concepts.

## Why this project

IFRS 9 (and the equivalent UK-adopted standard) requires lenders to recognise expected — not just
incurred — credit losses, staged according to how much credit risk has changed since origination.
This means every modern UK lender needs a working pipeline that can:

1. Score borrowers for **Probability of Default**,
2. Use that PD (plus arrears/credit-history triggers) to assign an **IFRS 9 stage**, and
3. Translate that staging into a **monetary loss provision** — `ECL = PD × LGD × EAD` — under both
   base-case and stressed macroeconomic scenarios.

This project builds that pipeline from the ground up on a real, historical loan dataset.

## Data

**Source:** Statlog (German Credit Data) — 1,000 real loan applications collected by
Prof. Hans Hofmann (Universität Hamburg), one of the most widely used benchmark datasets in
academic and industry credit-scoring research, hosted on the UCI Machine Learning Repository.

This project uses a **536-row extract of the genuine dataset** — every row is a real, historical
loan application with a real recorded good/bad outcome (not synthetic data). The raw "A-coded"
categorical fields (e.g. `A11`, `A34`) are mapped to human-readable labels using the dataset's
official attribute documentation (`german.names`), and the target is recoded into a standard
**`default_flag`** (1 = defaulted, 0 = repaid in full).

| File | Description |
|---|---|
| `data/german_credit_raw.csv` | Raw extract — 536 real records, original A-coded fields |
| `data/build_clean_dataset.py` | Script that maps A-codes → readable labels and recodes the target |
| `data/german_credit_data.csv` | Cleaned, analysis-ready dataset (536 rows × 21 columns) used by the notebook |

**Headline statistics:** 536 accounts, **27.6% historical default rate**, 20 borrower-level
features covering financial history (checking/savings account status, credit history, existing
credits), loan characteristics (purpose, amount, duration, instalment rate), and demographic /
employment factors (age, job, employment length, housing, property).

> **Honest scope note:** the underlying loans are German rather than British, but the **modelling
> framework, IFRS 9 staging logic, and ECL mechanics demonstrated here are identical** to those
> used by UK lenders — which is exactly why German Credit Data remains a standard benchmark for
> credit-scoring research. The cost-matrix, LGD and macroeconomic-stress assumptions used in this
> notebook are illustrative, simplified for demonstration, and would need recalibration against a
> lender's own loss history before any production use.

## Methodology

### 1. Probability of Default (PD) modelling
Two models are trained and compared — a benchmark/challenger pattern used widely in bank model
validation:

- **Logistic Regression** — interpretable "scorecard-style" benchmark; coefficients translate
  directly into points-based scorecards that credit committees and regulators can scrutinise.
- **Gradient Boosting** — a non-linear ensemble "challenger" model that typically improves
  discrimination at the cost of interpretability.

Both are validated using the metrics most commonly required in PD model validation packs:
**AUC** (overall discrimination), the **KS statistic** (maximum separation between cumulative
good/bad distributions), and a **calibration curve** (because ECL depends on the *level* of PD,
not just its rank-ordering — a well-discriminating but poorly-calibrated model would still
misstate provisions).

### 2. IFRS 9 staging (Stage 1 / Stage 2 / Stage 3)
Each account is classified into one of three IFRS 9 stages, which determines the ECL horizon:

| Stage | Meaning | ECL basis |
|---|---|---|
| **Stage 1** | Performing — no significant increase in credit risk (SICR) | 12-month ECL |
| **Stage 2** | Underperforming — SICR identified | Lifetime ECL |
| **Stage 3** | Credit-impaired / in default | Lifetime ECL + specific provisioning |

In the absence of origination-date PDs, **SICR is proxied** using a "backstop + relative PD
deterioration" approach widely used in practice: accounts are flagged Stage 2 if their modelled PD
crosses a watchlist threshold *or* they carry adverse credit-history flags (e.g. "delay in paying
off in the past"), and flagged Stage 3 if they are already in default — mirroring the 90-days-past-
due regulatory backstop used across UK/EU banks.

### 3. Expected Credit Loss (ECL) calculation
Account-level ECL is computed as:

```
ECL = PD × LGD × EAD
```

- **PD** — the modelled 12-month PD; for Stage 2/3 accounts a simplified lifetime-PD scalar is
  applied (in production, this would come from a survival/term-structure model).
- **LGD (Loss Given Default)** — illustrative assumptions that vary by collateral position
  (real estate / savings & insurance / other assets / unsecured), consistent with how secured vs.
  unsecured retail exposures are typically differentiated.
- **EAD (Exposure at Default)** — approximated by the outstanding loan balance, a standard
  simplification for term loans without revolving drawdown risk.

### 4. Macroeconomic stress overlay
IFRS 9 requires forward-looking, scenario-weighted ECL — not just point-in-time estimates. The
notebook applies an illustrative **downside stress multiplier** to PDs (representing, e.g., rising
unemployment and falling asset prices, in the spirit of a Bank of England annual cyclical scenario)
and compares **base-case vs. stressed ECL** at both account and portfolio level.

## Results (test sample, 134 accounts)

| Model | AUC | KS statistic |
|---|---|---|
| Logistic Regression | 0.737 | 0.409 |
| **Gradient Boosting (selected)** | **0.738** | 0.405 |

| Stage | Accounts | Total exposure | Base-case ECL | Stressed ECL | Coverage (base → stressed) |
|---|---|---|---|---|---|
| Stage 1 | majority of book | — | — | — | lowest |
| Stage 2 | watchlist accounts | — | — | — | mid |
| Stage 3 | known defaults | — | — | — | highest |

**Portfolio summary (illustrative monetary units):**

- Total exposure (EAD): **417,022**
- Base-case ECL: **131,646** (31.6% coverage ratio)
- Stressed (downside) ECL: **139,802** (33.5% coverage ratio)
- ECL uplift under stress: **+6.2%**

*(Full stage-level breakdowns, charts, and the worked single-application scoring example are in
the notebook — see Sections 5–7.)*

## Worked example — scoring a new application

The notebook includes an end-to-end scoring walkthrough: take one applicant's profile, run it
through the production PD model, assign an IFRS 9 stage, and compute that account's individual ECL
contribution under both base and stressed scenarios — exactly the kind of output an underwriting or
provisioning system would produce operationally.

## Project structure

```
.
├── Credit_Risk_IFRS9_ECL_Model.ipynb   # Main notebook — full pipeline, charts, results
├── data/
│   ├── german_credit_raw.csv           # Raw extract (536 real records, A-coded)
│   ├── build_clean_dataset.py          # Cleans & relabels the raw data
│   └── german_credit_data.csv          # Analysis-ready dataset used by the notebook
├── requirements.txt
└── README.md
```

## How to run

```bash
# 1. Set up environment
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. (Optional) rebuild the cleaned dataset from the raw extract
cd data && python3 build_clean_dataset.py && cd ..

# 3. Launch the notebook
jupyter notebook Credit_Risk_IFRS9_ECL_Model.ipynb
```

The notebook runs top-to-bottom with no manual intervention and reproduces every table, chart and
metric in this README (random seed fixed at `42` for reproducibility).

## Extending this for production use

- Calibrate **LGD and EAD** against the lender's own historical workout/recovery data.
- Build a proper **lifetime PD term structure** (survival analysis / Markov transition matrices)
  rather than a flat lifetime-PD scaling factor.
- Incorporate **probability-weighted multiple macroeconomic scenarios** (base / upside / downside)
  rather than a single stress overlay, in line with IFRS 9 illustrative guidance.
- Add **Population Stability Index (PSI)** monitoring to detect PD model drift, and periodic
  back-testing of realised vs. predicted default and loss rates.
- Subject the model to **independent model validation** and governance sign-off, consistent with
  PRA SS1/23 (Model Risk Management) expectations for UK banks.

## Disclaimer

This is a learning/portfolio project. The cost-matrix, LGD and macroeconomic-stress parameters are
illustrative and simplified for demonstration purposes — they are **not** calibrated to any real
institution's loss experience and should not be used for actual provisioning decisions.
