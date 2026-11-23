"""Validation and calculations shared by the Streamlit app and its checks."""

import io
import json
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.stats.proportion import confint_proportions_2indep, proportions_ztest

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
ROOT = Path(__file__).resolve().parent


def read_users(content: bytes) -> pd.DataFrame:
    try:
        df = pd.read_csv(io.BytesIO(content))
    except (ValueError, UnicodeError, pd.errors.ParserError) as exc:
        raise ValueError("Upload a readable UTF-8 CSV file.") from exc
    required = {"user id", "test group", "converted", "total ads", "most ads day", "most ads hour"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError("Missing columns: " + ", ".join(sorted(missing)))
    df = df[sorted(required)].copy()
    if df.empty or df.isna().any().any():
        raise ValueError("The CSV must contain users and no missing values in the required columns.")
    if df["user id"].duplicated().any():
        raise ValueError("Each user id must occur once. Duplicate users were found.")
    if not df["test group"].isin(["ad", "psa"]).all():
        raise ValueError("Test group must be ad or psa.")
    converted = df["converted"].astype(str).str.strip().str.lower()
    if not converted.isin(["true", "false", "1", "0"]).all():
        raise ValueError("Converted must contain True/False or 1/0 values.")
    df["converted"] = converted.isin(["true", "1"]).astype(int)
    for column in ["total ads", "most ads hour"]:
        values = pd.to_numeric(df[column], errors="coerce")
        if not np.isfinite(values).all() or (values < 0).any() or (values % 1 != 0).any():
            raise ValueError(f"{column} must contain nonnegative whole numbers.")
        if (values > np.iinfo(np.int64).max).any():
            raise ValueError(f"{column} contains numbers that are too large.")
        df[column] = values.astype("int64")
    if (df["most ads hour"] > 23).any():
        raise ValueError("Most ads hour must be between 0 and 23.")
    if not df["most ads day"].isin(DAYS).all():
        raise ValueError("Most ads day must use full English day names, such as Monday.")
    return df


def aggregate(df: pd.DataFrame, cutoff: float) -> dict:
    """Compute SQL summaries without removing users or duplicate activity patterns."""
    with sqlite3.connect(":memory:") as conn:
        df.to_sql("users", conn, index=False)
        metric_sql = '"test group" AS test_group, COUNT(*) AS users, SUM(converted) AS conversions'
        overall = pd.read_sql_query(f"SELECT {metric_sql} FROM users GROUP BY 1", conn)
        day = pd.read_sql_query(
            f'SELECT "most ads day" AS day, {metric_sql} FROM users GROUP BY 1, 2', conn
        )
        hour = pd.read_sql_query(
            f'SELECT "most ads hour" AS hour, {metric_sql} FROM users GROUP BY 1, 2', conn
        )
        exposure = pd.read_sql_query(
            f"SELECT CASE WHEN \"total ads\" <= ? THEN 'Light' ELSE 'Heavy' END AS exposure, "
            f"{metric_sql} FROM users GROUP BY 1, 2", conn, params=(float(cutoff),)
        )
    return {"overall": overall, "day": day, "hour": hour, "exposure": exposure, "cutoff": cutoff}


def saved_results() -> dict:
    snapshot = json.loads((ROOT / "results_snapshot.json").read_text(encoding="utf-8"))
    return {**snapshot, **{key: pd.DataFrame(snapshot[key]) for key in ["overall", "day", "hour", "exposure"]}}


def rates(table: pd.DataFrame) -> pd.DataFrame:
    table = table.copy()
    table["conversion_rate_pct"] = table["conversions"] / table["users"] * 100
    return table


def comparisons(table: pd.DataFrame, segment: str, order: list) -> pd.DataFrame:
    comparison = rates(table).pivot(index=segment, columns="test_group", values="conversion_rate_pct")
    comparison = comparison.reindex(index=order, columns=["ad", "psa"])
    comparison["difference_pp"] = comparison["ad"] - comparison["psa"]
    comparison["relative_lift_pct"] = comparison["difference_pp"] / comparison["psa"].replace(0, np.nan) * 100
    return comparison


def overall_metrics(table: pd.DataFrame) -> dict | None:
    indexed = table.set_index("test_group").reindex(["ad", "psa"])
    if indexed["users"].isna().any() or (indexed["users"] <= 0).any():
        return None
    counts = indexed["conversions"].to_numpy(dtype=int)
    users = indexed["users"].to_numpy(dtype=int)
    ad, psa = counts / users
    difference = ad - psa
    if counts.sum() in [0, users.sum()]:
        p_value = 1.0
    else:
        _, p_value = proportions_ztest(counts, users, alternative="two-sided")
    low, high = confint_proportions_2indep(
        count1=counts[0], nobs1=users[0], count2=counts[1], nobs2=users[1], method="newcomb", compare="diff"
    )
    return dict(ad=ad, psa=psa, difference=difference, lift=difference / psa * 100 if psa else None,
                p_value=p_value, ci_low=low, ci_high=high, additional=difference * users[0])


def roi_table(additional: float, cost: float, contribution: float) -> pd.DataFrame:
    inputs = [
        ("Conservative", 600000, 100), ("Moderate", 400000, 150),
        ("Optimistic", 200000, 200), ("Your scenario", cost, contribution)
    ]
    table = pd.DataFrame(inputs, columns=["Scenario", "Assumed spend (INR)", "Contribution per conversion (INR)"])
    table["Incremental contribution (INR)"] = additional * table["Contribution per conversion (INR)"]
    table["Net contribution (INR)"] = table["Incremental contribution (INR)"] - table["Assumed spend (INR)"]
    table["Estimated ROI (%)"] = table["Net contribution (INR)"] / table["Assumed spend (INR)"].replace(0, np.nan) * 100
    # A negative contribution cannot fund any nonnegative campaign spend.
    table["Break-even spend (INR)"] = table["Incremental contribution (INR)"].where(
        table["Incremental contribution (INR)"] >= 0
    )
    return table
