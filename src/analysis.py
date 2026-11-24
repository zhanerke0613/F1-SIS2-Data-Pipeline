from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
FIGURES_DIR = BASE_DIR / "figures"

FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def analyze_data():
    df = pd.read_csv(DATA_DIR / "processed_data.csv")

    # 1. General dataset information
    print("Dataset shape:", df.shape)
    print("Total records:", len(df))
    print("Total columns:", len(df.columns))

    print("\nData types:")
    print(df.dtypes)

    print("\nNumerical statistics:")
    print(df.describe().to_string())

    print("\nCategorical statistics:")
    print(df.describe(include=["object"]).to_string())

    # 2. Group analysis
    team_stats = df.groupby("constructor_name").agg(
        total_points=("points", "sum"),
        average_position=("position", "mean"),
        finish_rate=("finished", "mean"),
        total_records=("driver_id", "count")
    )

    team_stats["finish_rate"] *= 100

    print("\nConstructor statistics:")
    print(team_stats.to_string())

    team_stats.to_csv(DATA_DIR / "team_statistics.csv")

    # Chart 1: Total points by constructor
    team_points = df.groupby(
        "constructor_name"
    )["points"].sum().sort_values()

    plt.figure(figsize=(11, 6))

    team_points.plot(
        kind="barh",
        color="royalblue",
        label="Race points"
    )

    plt.title("F1 2024: Race Points by Constructor")
    plt.xlabel("Total Race Points")
    plt.ylabel("Constructor")
    plt.legend()
    plt.tight_layout()

    plt.savefig(
        FIGURES_DIR / "01_team_points.png",
        dpi=300
    )

    plt.close()

    # Chart 2: Starting vs finishing position
    plt.figure(figsize=(10, 6))

    grid_data = df[df["grid"] > 0]

    plt.scatter(
        grid_data["grid"],
        grid_data["position"],
        alpha=0.5,
        color="darkorange",
        label="Race result"
    )

    plt.plot(
        [1, 20],
        [1, 20],
        linestyle="--",
        color="gray",
        label="Same position"
    )

    plt.title("Starting Position vs Finishing Position")
    plt.xlabel("Starting Grid Position")
    plt.ylabel("Finishing Position")
    plt.legend()
    plt.grid(alpha=0.2)
    plt.tight_layout()

    plt.savefig(
        FIGURES_DIR / "02_grid_vs_position.png",
        dpi=300
    )

    plt.close()

    # Chart 3: Finished vs not finished by constructor
    finish_stats = pd.crosstab(
        df["constructor_name"],
        df["finished"],
        normalize="index"
    ) * 100

    finish_stats = finish_stats.reindex(
        columns=[1, 0],
        fill_value=0
    )

    finish_stats.columns = ["Finished", "Not finished"]

    finish_stats.plot(
        kind="bar",
        stacked=True,
        figsize=(12, 6),
        color=["seagreen", "tomato"]
    )

    plt.title("Race Completion Rate by Constructor")
    plt.xlabel("Constructor")
    plt.ylabel("Percentage of Race Results (%)")
    plt.xticks(rotation=45, ha="right")
    plt.legend()
    plt.tight_layout()

    plt.savefig(
        FIGURES_DIR / "03_finish_rate.png",
        dpi=300
    )

    plt.close()

    print("\nEDA completed successfully.")
    print("Three charts saved to figures/")
    print("Team statistics saved to data/team_statistics.csv")

    return team_stats


if __name__ == "__main__":
    analyze_data()