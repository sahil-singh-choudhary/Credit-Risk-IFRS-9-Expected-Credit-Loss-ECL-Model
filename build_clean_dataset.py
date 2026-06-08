"""
Builds a cleaned, human-readable version of the Statlog (German Credit Data) dataset.

Source: Prof. Hans Hofmann, University of Hamburg / UCI Machine Learning Repository
Original encoding uses categorical "A-codes" (e.g. A11, A34) — this script maps
each code to a readable label using the official attribute documentation
(german.names) and writes a cleaned CSV ready for analysis.
"""

import pandas as pd

RAW_PATH = "german_credit_raw.csv"
OUT_PATH = "german_credit_data.csv"

COLUMNS = [
    "checking_account_status", "duration_months", "credit_history", "purpose",
    "credit_amount", "savings_account", "employment_since", "installment_rate_pct",
    "personal_status_sex", "other_debtors_guarantors", "residence_since", "property",
    "age_years", "other_installment_plans", "housing", "existing_credits_at_bank",
    "job", "num_dependents", "telephone", "foreign_worker", "target"
]

MAPS = {
    "checking_account_status": {
        "A11": "< 0 DM", "A12": "0 to < 200 DM", "A13": ">= 200 DM / salary assigned",
        "A14": "no checking account",
    },
    "credit_history": {
        "A30": "no credits taken / all paid duly",
        "A31": "all credits at this bank paid duly",
        "A32": "existing credits paid duly till now",
        "A33": "delay in paying off in the past",
        "A34": "critical account / other credits existing",
    },
    "purpose": {
        "A40": "car (new)", "A41": "car (used)", "A42": "furniture/equipment",
        "A43": "radio/television", "A44": "domestic appliances", "A45": "repairs",
        "A46": "education", "A47": "vacation", "A48": "retraining", "A49": "business",
        "A410": "other",
    },
    "savings_account": {
        "A61": "< 100 DM", "A62": "100 to < 500 DM", "A63": "500 to < 1000 DM",
        "A64": ">= 1000 DM", "A65": "unknown / no savings account",
    },
    "employment_since": {
        "A71": "unemployed", "A72": "< 1 year", "A73": "1 to < 4 years",
        "A74": "4 to < 7 years", "A75": ">= 7 years",
    },
    "personal_status_sex": {
        "A91": "male: divorced/separated", "A92": "female: divorced/separated/married",
        "A93": "male: single", "A94": "male: married/widowed", "A95": "female: single",
    },
    "other_debtors_guarantors": {
        "A101": "none", "A102": "co-applicant", "A103": "guarantor",
    },
    "property": {
        "A121": "real estate", "A122": "building society savings / life insurance",
        "A123": "car or other (not in savings)", "A124": "unknown / no property",
    },
    "other_installment_plans": {
        "A141": "bank", "A142": "stores", "A143": "none",
    },
    "housing": {
        "A151": "rent", "A152": "own", "A153": "for free",
    },
    "job": {
        "A171": "unemployed / unskilled non-resident", "A172": "unskilled resident",
        "A173": "skilled employee / official", "A174": "management/self-employed/highly qualified",
    },
    "telephone": {
        "A191": "none", "A192": "registered under customer's name",
    },
    "foreign_worker": {
        "A201": "yes", "A202": "no",
    },
}

df = pd.read_csv(RAW_PATH, header=None, names=COLUMNS)

for col, mapping in MAPS.items():
    df[col] = df[col].map(mapping)

# Original target: 1 = good credit risk, 2 = bad credit risk
# Recode to a standard "default flag" (1 = bad / defaulted, 0 = good) used throughout the notebook
df["default_flag"] = (df["target"] == 2).astype(int)
df = df.drop(columns=["target"])

df.to_csv(OUT_PATH, index=False)
print(f"Wrote {len(df)} rows to {OUT_PATH}")
print(df.head(3).T)
print("\nDefault rate:", df["default_flag"].mean().round(4))
