#!/usr/bin/env python3
"""Extract all California storm events (all years) from NOAA Storm Events.

Pulls the per-year `details` and `locations` gzipped CSVs, filters details to
California, left-joins locations on EVENT_ID (one row per location point), and
writes a single combined CSV.

Source: https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/
"""

import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import requests

BASE_URL = "https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/"
RAW_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw_data")
OUTPUT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "california_storm_events_1950_2026.csv",
)
HEADERS = {"User-Agent": "ca-storm-events-extract/1.0 (research)"}

# Columns that exist in details, so EVENT_ID/EPISODE_ID join keys stay text.
STR_COLS = {"EVENT_ID": "string", "EPISODE_ID": "string"}

# Location-only columns to keep, prefixed LOC_ to avoid clashing with details'
# own BEGIN_*/END_* range/location/lat-lon fields.
LOC_KEEP = [
    "EVENT_ID",  # join key (dropped from output suffix logic below)
    "LOCATION_INDEX",
    "RANGE",
    "AZIMUTH",
    "LOCATION",
    "LATITUDE",
    "LONGITUDE",
    "LAT2",
    "LON2",
]


def scrape_index():
    """Return {('details'|'locations'): {year:int -> filename}}."""
    resp = requests.get(BASE_URL, headers=HEADERS, timeout=60)
    resp.raise_for_status()
    files = {"details": {}, "locations": {}}
    pat = re.compile(
        r'href="(StormEvents_(details|locations)-ftp_v1\.0_d(\d{4})_c\d+\.csv\.gz)"'
    )
    for fname, ftype, year in pat.findall(resp.text):
        files[ftype][int(year)] = fname
    return files


def download(fname, retries=5):
    """Download fname into RAW_DIR if not already cached; return local path.

    Retries on transient network failures with exponential backoff so a single
    blip does not abort the whole run.
    """
    path = os.path.join(RAW_DIR, fname)
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return path
    url = BASE_URL + fname
    tmp = path + ".part"
    last_err = None
    for attempt in range(retries):
        try:
            with requests.get(url, headers=HEADERS, timeout=300, stream=True) as r:
                r.raise_for_status()
                with open(tmp, "wb") as fh:
                    for chunk in r.iter_content(chunk_size=1 << 16):
                        fh.write(chunk)
            os.rename(tmp, path)
            return path
        except (requests.exceptions.RequestException, OSError) as e:
            last_err = e
            if os.path.exists(tmp):
                try:
                    os.remove(tmp)
                except OSError:
                    pass
            time.sleep(min(2 ** attempt, 30))
    raise RuntimeError(f"Failed to download {fname} after {retries} attempts: {last_err}")


def main():
    os.makedirs(RAW_DIR, exist_ok=True)

    print("Scraping directory index ...")
    files = scrape_index()
    det = files["details"]
    loc = files["locations"]
    years = sorted(det)
    print(
        f"Found {len(det)} details files and {len(loc)} locations files; "
        f"years {years[0]}-{years[-1]}"
    )

    # Download everything (cached) in parallel.
    to_get = list(det.values()) + list(loc.values())
    print(f"Ensuring {len(to_get)} files are downloaded into {RAW_DIR} ...")
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(download, f): f for f in to_get}
        done = 0
        for fut in as_completed(futs):
            fut.result()  # raise on failure
            done += 1
            if done % 25 == 0 or done == len(to_get):
                print(f"  downloaded {done}/{len(to_get)}")

    per_year = []
    total_ca_events = 0
    total_loc_rows = 0

    for year in years:
        det_path = os.path.join(RAW_DIR, det[year])
        d = pd.read_csv(
            det_path, compression="gzip", dtype=STR_COLS, low_memory=False
        )
        mask = d["STATE"].astype("string").str.strip().str.upper() == "CALIFORNIA"
        ca = d[mask].copy()
        n_events = len(ca)
        total_ca_events += n_events
        if n_events == 0:
            print(f"  {year}: 0 CA events")
            continue

        ca_ids = set(ca["EVENT_ID"].dropna())

        n_loc = 0
        if year in loc:
            l = pd.read_csv(
                os.path.join(RAW_DIR, loc[year]),
                compression="gzip",
                dtype=STR_COLS,
                low_memory=False,
            )
            l = l[l["EVENT_ID"].isin(ca_ids)].copy()
            keep = [c for c in LOC_KEEP if c in l.columns]
            l = l[keep]
            rename = {
                c: f"LOC_{c}" for c in keep if c != "EVENT_ID"
            }
            l = l.rename(columns=rename)
            n_loc = len(l)
            merged = ca.merge(l, on="EVENT_ID", how="left")
        else:
            merged = ca.copy()

        total_loc_rows += n_loc
        per_year.append(merged)
        print(f"  {year}: {n_events} CA events, {n_loc} location rows")

    print("Concatenating ...")
    combined = pd.concat(per_year, ignore_index=True)

    sort_cols = [c for c in ["YEAR", "EVENT_ID", "LOC_LOCATION_INDEX"] if c in combined]
    combined = combined.sort_values(sort_cols, kind="stable").reset_index(drop=True)

    combined.to_csv(OUTPUT, index=False)

    # ---- verification ----
    assert (combined["STATE"].str.strip().str.upper() == "CALIFORNIA").all()
    if "STATE_FIPS" in combined:
        fips = pd.to_numeric(combined["STATE_FIPS"], errors="coerce")
        assert (fips == 6).all(), "Non-CA STATE_FIPS found"
    distinct_events = combined["EVENT_ID"].nunique()

    print("\n=== Summary ===")
    print(f"CA events found in details : {total_ca_events}")
    print(f"Distinct EVENT_IDs in output: {distinct_events}")
    print(f"Location rows joined        : {total_loc_rows}")
    print(f"Total output rows           : {len(combined)}")
    print(f"Columns                     : {len(combined.columns)}")
    print(f"Year coverage               : {combined['YEAR'].min()}-{combined['YEAR'].max()}")
    print(f"Output written              : {OUTPUT}")


if __name__ == "__main__":
    sys.exit(main())
