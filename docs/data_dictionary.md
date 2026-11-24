# Data Dictionary — F1 2024

Source: Jolpica F1 API

Raw dataset: 479 records, 17 columns.
Processed dataset: 479 records, 19 columns.

| Column | Data Type | Description | Example |
|---|---|---|---|
| season | Integer | Championship year | 2024 |
| round | Integer | Race round number | 1 |
| race_name | String | Name of the race | Bahrain Grand Prix |
| race_date | Date | Date of the race | 2024-03-02 |
| circuit_id | String | Unique circuit identifier | bahrain |
| country | String | Host country | Bahrain |
| driver_id | String | Unique driver identifier | max_verstappen |
| driver_name | String | Full name of the driver | Max Verstappen |
| constructor_id | String | Unique team identifier | red_bull |
| constructor_name | String | Normalized team name | red bull |
| grid | Integer | Starting position | 1 |
| position | Integer | Result position | 1 |
| points | Float | Race points earned | 26.0 |
| laps | Integer | Completed laps | 57 |
| status | String | Race result status | finished |
| race_time_ms | Nullable Integer | Race time in milliseconds | 5456398 |
| fastest_lap_time | Nullable String | Fastest lap time | 1:32.608 |
| finished | Integer | Completion indicator: 1 or 0 | 1 |
| positions_gained | Nullable Float | Grid minus result position | 3.0 |

## Primary Key

The composite primary key consists of season, round, and driver_id.

## Missing Values

- race_time_ms: 47 missing values.
- fastest_lap_time: 17 missing values.
- positions_gained: 1 missing value because grid is zero.
- Missing values are preserved to avoid introducing artificial data.

## Derived Columns

- finished: 1 for finished or lapped, otherwise 0.
- positions_gained: grid minus position. Null when grid is zero.

## Validation Rules

- Season must be 2024.
- Round must be between 1 and 24.
- Points must be between 0 and 26.
- Grid must be between 0 and 30.
- Laps cannot be negative.
- Race date must be within 2024.
- Driver and constructor IDs are required.
- Composite primary key must be unique.

## Validation Results

479 valid records and 3 intentionally invalid test records. Test records are excluded from the final dataset.