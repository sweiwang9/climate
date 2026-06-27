# Codebook — `california_storm_events_1950_2026.csv`

One row per **(California storm event × location point)**. Columns 1–51 come from
NOAA's Storm Events **details** file (event-level; values repeat across an event's
location rows). Columns 52–59 (`LOC_*`) come from the **locations** file (one per
location point); they are blank for events with no location record.

Source documentation:
https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/Storm-Data-Bulk-csv-Format.pdf
and https://www.ncdc.noaa.gov/stormevents/

Notes on types: all fields were read/written as text to preserve source
formatting (e.g. damage codes like `2.5M`, leading zeros, mixed integer/float
display such as `6.0`). Cast as needed for analysis.

---

## Event identifiers & timing (from details)

| # | Variable | Type | Description |
|---|----------|------|-------------|
| 1 | `BEGIN_YEARMONTH` | int (YYYYMM) | Year and month the event began. |
| 2 | `BEGIN_DAY` | int | Day of month the event began. |
| 3 | `BEGIN_TIME` | int (HHMM) | Local time the event began, 24-hour `HHMM`. |
| 4 | `END_YEARMONTH` | int (YYYYMM) | Year and month the event ended. |
| 5 | `END_DAY` | int | Day of month the event ended. |
| 6 | `END_TIME` | int (HHMM) | Local time the event ended, 24-hour `HHMM`. |
| 7 | `EPISODE_ID` | int | ID of the **episode** — a set of related events caused by the same weather system (a storm system can spawn many events). Links events together; not unique per row. |
| 8 | `EVENT_ID` | int | Unique ID of the individual storm **event**. Primary join key to the locations file. Unique per event (repeats across that event's location rows). |
| 18 | `BEGIN_DATE_TIME` | datetime | Event start as `DD-MON-YY HH:MM:SS` (local). |
| 20 | `END_DATE_TIME` | datetime | Event end as `DD-MON-YY HH:MM:SS` (local). |
| 19 | `CZ_TIMEZONE` | string | Time zone of the times above (e.g. `PST`, `PDT`, occasionally `CST`/`MST` for the zone-based record). |
| 11 | `YEAR` | int | Calendar year of the event. |
| 12 | `MONTH_NAME` | string | Month name of the event (`January` … `December`). |

## Location / geography (from details)

| # | Variable | Type | Description |
|---|----------|------|-------------|
| 9 | `STATE` | string | State name — always `CALIFORNIA` in this file. |
| 10 | `STATE_FIPS` | int | State FIPS code — `6` for California. |
| 14 | `CZ_TYPE` | char | Geographic unit type of the record: `C` = county/parish (FIPS), `Z` = NWS public forecast zone, `M` = marine zone. |
| 15 | `CZ_FIPS` | int | County FIPS code (when `CZ_TYPE=C`) or forecast-zone number (when `Z`/`M`). |
| 16 | `CZ_NAME` | string | County or zone name (e.g. `LOS ANGELES`, `SANTA CLARA`). |
| 17 | `WFO` | string | NWS Weather Forecast Office that issued the record (e.g. `LOX`, `STO`). |
| 39 | `BEGIN_RANGE` | float | Distance (miles) from the reference point named in `BEGIN_LOCATION` to where the event began. |
| 40 | `BEGIN_AZIMUTH` | string | Compass direction (e.g. `ENE`, `SW`) from the reference point to the event begin location. |
| 41 | `BEGIN_LOCATION` | string | Name of the nearest reference place/landmark for the event begin point. |
| 42 | `END_RANGE` | float | Distance (miles) from the reference point in `END_LOCATION` to where the event ended. |
| 43 | `END_AZIMUTH` | string | Compass direction from the reference point to the event end location. |
| 44 | `END_LOCATION` | string | Name of the nearest reference place/landmark for the event end point. |
| 45 | `BEGIN_LAT` | float | Latitude (decimal degrees) where the event began. |
| 46 | `BEGIN_LON` | float | Longitude (decimal degrees) where the event began (negative = west). |
| 47 | `END_LAT` | float | Latitude (decimal degrees) where the event ended. |
| 48 | `END_LON` | float | Longitude (decimal degrees) where the event ended. |

## Event classification & impacts (from details)

| # | Variable | Type | Description |
|---|----------|------|-------------|
| 13 | `EVENT_TYPE` | string | Type of weather event (e.g. `Tornado`, `Thunderstorm Wind`, `Hail`, `Flash Flood`, `Wildfire`, `High Wind`). Controlled vocabulary from NWS Directive 10-1605. |
| 21 | `INJURIES_DIRECT` | int | Injuries directly caused by the event. |
| 22 | `INJURIES_INDIRECT` | int | Injuries indirectly attributable to the event. |
| 23 | `DEATHS_DIRECT` | int | Deaths directly caused by the event. (Per-death detail is in NOAA's separate fatalities file, not merged here.) |
| 24 | `DEATHS_INDIRECT` | int | Deaths indirectly attributable to the event. |
| 25 | `DAMAGE_PROPERTY` | string (coded) | Estimated property damage as a magnitude code: `K`=thousands, `M`=millions, `B`=billions (e.g. `2.5M` = $2,500,000). `0`/`0K`/blank = none/unknown. Parse the suffix to get dollars. |
| 26 | `DAMAGE_CROPS` | string (coded) | Estimated crop damage, same `K`/`M`/`B` coding as `DAMAGE_PROPERTY`. |
| 27 | `SOURCE` | string | Source of the report (e.g. `TRAINED SPOTTER`, `NEWSPAPER`, `OFFICIAL NWS OBS.`, `GENERAL PUBLIC`, `EMERGENCY MNGR`). |
| 28 | `MAGNITUDE` | float | Measured magnitude — wind speed in knots (for wind events) or hail diameter in inches (for hail). Blank for event types with no magnitude. |
| 29 | `MAGNITUDE_TYPE` | string | How `MAGNITUDE` was derived: `EG`=estimated gust, `MG`=measured gust, `ES`=estimated sustained, `MS`=measured sustained, `M`=measured, `E`=estimated. |
| 30 | `FLOOD_CAUSE` | string | Reported cause for flood-type events (e.g. `Heavy Rain`, `Heavy Rain / Burn Area`, `Dam / Levee Break`). Blank for non-flood events. |
| 31 | `CATEGORY` | string | Reserved/rarely populated category field (largely empty). |

## Tornado-specific (from details; populated only for tornado events)

| # | Variable | Type | Description |
|---|----------|------|-------------|
| 32 | `TOR_F_SCALE` | string | Fujita (`F0`–`F5`) or Enhanced Fujita (`EF0`–`EF5`) intensity rating. |
| 33 | `TOR_LENGTH` | float | Tornado path length in miles. |
| 34 | `TOR_WIDTH` | float | Tornado path width in yards. |
| 35 | `TOR_OTHER_WFO` | string | If the tornado crossed into another WFO's area, that office's ID. |
| 36 | `TOR_OTHER_CZ_STATE` | string | State of the segment continued in another county/zone. |
| 37 | `TOR_OTHER_CZ_FIPS` | int | County FIPS of that continued segment. |
| 38 | `TOR_OTHER_CZ_NAME` | string | County name of that continued segment. |

## Narratives & provenance (from details)

| # | Variable | Type | Description |
|---|----------|------|-------------|
| 49 | `EPISODE_NARRATIVE` | text | Free-text description of the overall episode (the broader weather situation). Same text repeats for all events in an episode. |
| 50 | `EVENT_NARRATIVE` | text | Free-text description specific to this individual event. |
| 51 | `DATA_SOURCE` | string | Provenance of the record in NOAA's archive. Observed values in this file: `CSV`, `PDS`, `PDC`, `PUB` (see appendix). |

## Location-point detail (from the locations file — prefixed `LOC_`)

One set of these per location point of an event; blank when the event has no
location record. The `LOC_` prefix avoids clashing with the details `BEGIN_*`/
`END_*` fields above.

| # | Variable | Type | Description |
|---|----------|------|-------------|
| 52 | `LOC_LOCATION_INDEX` | int | Sequence number of this location point within the event (1, 2, 3, … in path order). |
| 53 | `LOC_RANGE` | float | Distance (miles) from the reference place in `LOC_LOCATION` to this point. |
| 54 | `LOC_AZIMUTH` | string | Compass direction from that reference place to this point. |
| 55 | `LOC_LOCATION` | string | Name of the nearest reference place/landmark for this point. |
| 56 | `LOC_LATITUDE` | float | Latitude of this point in decimal degrees. |
| 57 | `LOC_LONGITUDE` | float | Longitude of this point in decimal degrees (negative = west). |
| 58 | `LOC_LAT2` | int | Raw NOAA latitude in degrees-and-hundredths-of-minutes (`DDMM` × 100 style, e.g. `4157` ≈ 41°57′); legacy companion to `LOC_LATITUDE`. |
| 59 | `LOC_LON2` | int | Raw NOAA longitude in the same packed format (e.g. `12410` ≈ 124°10′W). |

---

## Practical tips

- **Counting events vs. rows:** use distinct `EVENT_ID` for event counts; raw row
  counts over-count events that have multiple location points.
- **Damage to dollars:** strip the trailing `K`/`M`/`B` from `DAMAGE_PROPERTY` /
  `DAMAGE_CROPS` and multiply by 1e3 / 1e6 / 1e9.
- **Geocoordinates:** prefer `LOC_LATITUDE`/`LOC_LONGITUDE` (decimal degrees) for
  mapping; `BEGIN_LAT`/`BEGIN_LON` give the single event begin point.
- **Fatality detail** (age, sex, location of each death) lives in NOAA's separate
  fatalities file and was intentionally not merged; this file carries only the
  `DEATHS_DIRECT` / `DEATHS_INDIRECT` counts. (The raw fatalities `.gz` files are
  nonetheless cached in `raw_data/` for future use.)

---

## Appendix — observed values in this file (cross-checked)

Counts below are over all **59,577 rows** (event values repeat across an event's
location rows), generated from the actual CSV. Use them to validate decoding.

### `CZ_TYPE` (2 values)
Only county and zone records are present — no marine (`M`).

| Value | Meaning | Rows |
|-------|---------|------|
| `C` | County/parish (FIPS) | 31,796 |
| `Z` | NWS public forecast zone | 27,781 |

### `MAGNITUDE_TYPE` (6 values)
Matches the NOAA spec exactly.

| Value | Meaning | Rows |
|-------|---------|------|
| `MG` | Measured gust | 6,756 |
| `EG` | Estimated gust | 2,478 |
| `M` | Measured | 280 |
| `E` | Estimated | 153 |
| `MS` | Measured sustained | 117 |
| `ES` | Estimated sustained | 17 |

(Blank for event types with no magnitude.)

### `DATA_SOURCE` (4 values)
NOAA archive-provenance codes.

| Value | Rows | Note |
|-------|------|------|
| `CSV` | 49,775 | Ingested from CSV submission |
| `PDS` | 5,488 | NOAA internal provenance code |
| `PDC` | 3,841 | NOAA internal provenance code |
| `PUB` | 473 | Legacy *Storm Data* publication |

### `TOR_F_SCALE` (8 values; tornado events only)
Mix of legacy Fujita (`F*`) and Enhanced Fujita (`EF*`).

| Value | Rows | | Value | Rows |
|-------|------|---|-------|------|
| `F0` | 222 | | `EF1` | 48 |
| `EF0` | 162 | | `F2` | 22 |
| `F1` | 90 | | `EFU` (EF unknown) | 8 |
| | | | `EF2` | 6 |
| | | | `F3` | 2 |

### `FLOOD_CAUSE` (7 values; flood-type events only)

| Value | Rows |
|-------|------|
| `Heavy Rain` | 21,817 |
| `Heavy Rain / Burn Area` | 1,080 |
| `Heavy Rain / Tropical System` | 408 |
| `Heavy Rain / Snow Melt` | 259 |
| `Dam / Levee Break` | 111 |
| `Planned Dam Release` | 67 |
| `Ice Jam` | 4 |

### `CATEGORY`
**Always empty** in this file (0 non-null values). Reserved/unused for CA.

### `DAMAGE_PROPERTY` / `DAMAGE_CROPS` suffix codes (observed)
Confirms the `K`/`M`/`B` decoding used to build the `_USD` columns. One crop value
`0T` appears (legacy `T`=thousand, but the amount is 0).

| Suffix | Property rows | Crops rows | Multiplier |
|--------|---------------|------------|------------|
| `K` | 48,271 | 47,484 | ×1,000 |
| `M` | 929 | 179 | ×1,000,000 |
| `B` | 4 | 1 | ×1,000,000,000 |
| `T` | 0 | 1 | ×1,000 (legacy) |
| (none) | 820 | 623 | literal dollars (mostly `0`) |

### `SOURCE` (66 distinct values)
High cardinality, and the **same source appears in two casings** because NOAA
changed style over time — e.g. `Law Enforcement` (15,544) vs `LAW ENFORCEMENT`
(547); `Trained Spotter` vs `TRAINED SPOTTER`; `Newspaper` vs `NEWSPAPER`. Normalize
case before grouping. Most common: `Law Enforcement`, `Mesonet`, `Department of
Highways`, `Public`, `Trained Spotter`, `ASOS`, `RAWS`, `Broadcast Media`,
`Newspaper`, `Emergency Manager`.

### `EVENT_TYPE` (40 distinct values)
All values present, by frequency:

`Flood` (14,311), `Flash Flood` (8,250), `High Wind` (7,119), `Heavy Snow`
(3,761), `Debris Flow` (2,690), `Dense Fog` (2,441), `Strong Wind` (2,375),
`Heavy Rain` (2,279), `Drought` (1,870), `Winter Storm` (1,660), `Wildfire`
(1,590), `Thunderstorm Wind` (1,502), `Frost/Freeze` (1,501), `Excessive Heat`
(1,481), `Winter Weather` (1,475), `Heat` (1,200), `Hail` (1,015), `Tornado`
(598), `High Surf` (500), `Funnel Cloud` (474), `Lightning` (374), `Dust Storm`
(234), `Cold/Wind Chill` (193), `Coastal Flood` (120), `Extreme Cold/Wind Chill`
(119), `Rip Current` (116), `Avalanche` (56), `Waterspout` (44), `Blizzard`
(44), `Dense Smoke` (35), `Storm Surge/Tide` (32), `Tropical Storm` (23), `Dust
Devil` (21), `Tsunami` (21), `Sneakerwave` (20), `Astronomical Low Tide` (17),
`Ice Storm` (7), `Freezing Fog` (7), `Marine High Wind` (1), `Lake-Effect Snow`
(1).
