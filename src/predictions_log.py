"""
predictions_log.py — PastureIQ Group G: the predictions log.

Records every forecast the tool makes (date_made, region, horizon, variable, predicted_value,
confidence, target_date). Once target_date arrives, record_actual() back-fills the real
observed value and the resulting error. This module is infrastructure only — it does NOT apply
bias correction itself (see FORMULAS.md Group G, Step 4); it gives that later step something
honest to read from.

Enables:
  - a public, checkable accuracy track record (farmer trust + capstone evidence)
  - future bias correction: corrected_prediction = raw_prediction - mean(recent error)

Source: FORMULAS.md Group G. Schema is fixed here — do not change columns without updating
both this file and data/predictions/predictions_log.csv's header.
"""

import csv
import os
from datetime import date

import pandas as pd

LOG_PATH = "data/predictions/predictions_log.csv"
COLUMNS = [
    "date_made", "region", "horizon_days", "variable", "predicted_value",
    "confidence", "target_date", "actual_value", "error",
]


def log_prediction(region, horizon_days, variable, predicted_value, confidence, target_date):
    """
    Append a new prediction row. actual_value and error are left blank — filled in later by
    record_actual() once target_date has passed and the real outcome is known.
    """
    row = {
        "date_made": date.today().isoformat(),
        "region": region,
        "horizon_days": horizon_days,
        "variable": variable,
        "predicted_value": predicted_value,
        "confidence": confidence,
        "target_date": target_date,
        "actual_value": "",
        "error": "",
    }
    file_exists = os.path.exists(LOG_PATH)
    with open(LOG_PATH, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def record_actual(region, variable, target_date, actual_value):
    """
    Back-fill actual_value + error for every matured prediction matching
    (region, variable, target_date) that hasn't already been filled. Intended to run as a
    scheduled job once target_date has passed (e.g. compare a 7-day rainfall forecast to the
    observed Open-Meteo value once that day arrives).
    """
    df = pd.read_csv(LOG_PATH, dtype=str)
    mask = (
        (df["region"] == region)
        & (df["variable"] == variable)
        & (df["target_date"] == target_date)
        & (df["actual_value"].isna() | (df["actual_value"] == ""))
    )
    df.loc[mask, "actual_value"] = str(actual_value)
    error_value = df.loc[mask, "predicted_value"].astype(float) - float(actual_value)
    df.loc[mask, "error"] = error_value.astype(str)
    df.to_csv(LOG_PATH, index=False)


def running_bias(region, variable, horizon_days, n=10):
    """
    Mean error over the last n matured predictions for (region, variable, horizon_days).
    Returns None if fewer than n matured predictions exist yet — deliberately refuses to
    correct on thin data rather than applying a noisy adjustment.
    Source: FORMULAS.md Group G, Step 3.
    """
    df = pd.read_csv(LOG_PATH, dtype=str)
    matured = df[
        (df["region"] == region)
        & (df["variable"] == variable)
        & (df["horizon_days"].astype(str) == str(horizon_days))
        & (df["error"].notna() & (df["error"] != ""))
    ].tail(n)
    if len(matured) < n:
        return None
    return matured["error"].astype(float).mean()