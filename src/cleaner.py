from pathlib import Path

import pandas as pd
import numpy as np

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def clean_data():
    df = pd.read_csv(DATA_DIR / "valid_records.csv")

    print("Records before cleaning:", len(df))
    print("\nMissing values before cleaning:")
    print(df.isna().sum())

    # Remove duplicate records
    df = df.drop_duplicates(
        subset=["season", "round", "driver_id"]
    ).copy()

    # Convert data types
    df["race_date"] = pd.to_datetime(df["race_date"])

    for column in ["season", "round", "grid", "position", "laps"]:
        df[column] = pd.to_numeric(df[column]).astype(int)

    df["points"] = pd.to_numeric(df["points"]).astype(float)

    df["race_time_ms"] = pd.to_numeric(
        df["race_time_ms"], errors="coerce"
    ).astype("Int64")

    # Normalize text
    df["status"] = df["status"].str.strip().str.lower()

    df["constructor_name"] = (
        df["constructor_name"].str.strip().str.lower()
    )

    df["driver_name"] = df["driver_name"].str.strip()

    # NumPy transformations
    df["finished"] = np.where(
        df["status"].isin(["finished", "lapped"]),
        1,
        0
    )

    df["positions_gained"] = np.where(
        df["grid"] > 0,
        df["grid"] - df["position"],
        np.nan
    )

    # Filter records using multiple conditions
    df = df[
        (df["season"] == 2024)
        & (df["points"] >= 0)
        & (df["laps"] >= 0)
    ].copy()

    # Grouping by constructor
    team_points = df.groupby("constructor_name")["points"].sum()
    team_points = team_points.sort_values(ascending=False)

    print("\nTotal points by constructor:")
    print(team_points)

    # Average positions gained by driver
    driver_stats = df.groupby("driver_name")["positions_gained"].mean()

    print("\nAverage positions gained:")
    print(driver_stats.sort_values(ascending=False))

    # Pivot table
    pivot = df.pivot_table(
        index="driver_name",
        columns="round",
        values="points",
        aggfunc="sum"
    )

    pivot.to_csv(DATA_DIR / "driver_points_pivot.csv")

    # Race completion statistics
    print("\nRace completion statistics:")
    print(df.groupby(["status", "finished"]).size())

    print("\nFinish rate:", round(df["finished"].mean() * 100, 2), "%")

    # Save processed data
    df.to_csv(DATA_DIR / "processed_data.csv", index=False)

    print("\nCleaning completed.")
    print("Records after cleaning:", len(df))
    print("Dataset shape:", df.shape)
    print("Saved: data/processed_data.csv")
    print("Saved: data/driver_points_pivot.csv")

    return df


if __name__ == "__main__":
    clean_data()