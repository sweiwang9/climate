#!/usr/bin/env python3
"""Add parsed USD damage columns to the California storm events dataset.

Reads the master CSV READ-ONLY and writes a NEW file (the master is never
modified). Adds:
  DAMAGE_PROPERTY_USD  - DAMAGE_PROPERTY parsed to dollars (float)
  DAMAGE_CROPS_USD     - DAMAGE_CROPS parsed to dollars (float)
  DAMAGE_TOTAL_USD     - sum of the two (NaN treated as 0 unless both missing)

NOAA encodes damage as a number with a magnitude suffix:
  K = thousand, M = million, B = billion (legacy: H = hundred, T = thousand).
  No suffix = the number is taken as literal dollars.
"""

import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "california_storm_events_1950_2026.csv")
DST = os.path.join(HERE, "california_storm_events_1950_2026_with_damage_usd.csv")

MULT = {"": 1, "H": 1e2, "K": 1e3, "T": 1e3, "M": 1e6, "B": 1e9}


def parse_damage(val):
    """Convert a NOAA damage code (e.g. '2.5M', '.25K', '0', '') to float USD."""
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return np.nan
    s = str(val).strip().upper()
    if s == "" or s == "NAN":
        return np.nan
    suffix = ""
    if s[-1] in MULT and not s[-1].isdigit():
        suffix = s[-1]
        s = s[:-1]
    s = s.replace(",", "").replace("$", "").strip()
    if s == "":
        s = "0"
    try:
        return float(s) * MULT[suffix]
    except (ValueError, KeyError):
        return np.nan


def main():
    df = pd.read_csv(SRC, dtype=str, low_memory=False)

    df["DAMAGE_PROPERTY_USD"] = df["DAMAGE_PROPERTY"].map(parse_damage)
    df["DAMAGE_CROPS_USD"] = df["DAMAGE_CROPS"].map(parse_damage)
    df["DAMAGE_TOTAL_USD"] = (
        df["DAMAGE_PROPERTY_USD"].fillna(0) + df["DAMAGE_CROPS_USD"].fillna(0)
    )
    # if both source values were missing, total should be NaN, not 0
    both_missing = df["DAMAGE_PROPERTY_USD"].isna() & df["DAMAGE_CROPS_USD"].isna()
    df.loc[both_missing, "DAMAGE_TOTAL_USD"] = np.nan

    df.to_csv(DST, index=False)

    print("Wrote:", DST)
    print("Rows:", len(df), "| Columns:", len(df.columns))
    print("\nParsed-value sanity check (per unique location-collapsed event rows):")
    print("  property USD  non-null:", df["DAMAGE_PROPERTY_USD"].notna().sum())
    print("  crops    USD  non-null:", df["DAMAGE_CROPS_USD"].notna().sum())
    print("  max property USD:", f"${df['DAMAGE_PROPERTY_USD'].max():,.0f}")
    print("  max crops    USD:", f"${df['DAMAGE_CROPS_USD'].max():,.0f}")
    # show a few code -> dollar mappings to eyeball correctness
    sample = (
        df[["DAMAGE_PROPERTY", "DAMAGE_PROPERTY_USD"]]
        .dropna()
        .drop_duplicates("DAMAGE_PROPERTY")
        .head(8)
    )
    print("\n  examples:")
    for code, usd in sample.itertuples(index=False):
        print(f"    {code:>8} -> ${usd:,.2f}")


if __name__ == "__main__":
    main()
