import sqlite3
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DB_PATH = DATA_DIR / "output.db"


def load_data():
    df = pd.read_csv(DATA_DIR / "processed_data.csv")

    with sqlite3.connect(DB_PATH) as conn:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS race_results (
                season INTEGER NOT NULL,
                round INTEGER NOT NULL,
                race_name TEXT,
                race_date TEXT,
                circuit_id TEXT,
                country TEXT,
                driver_id TEXT NOT NULL,
                driver_name TEXT,
                constructor_id TEXT,
                constructor_name TEXT,
                grid INTEGER,
                position INTEGER,
                points REAL,
                laps INTEGER,
                status TEXT,
                race_time_ms INTEGER,
                fastest_lap_time TEXT,
                finished INTEGER,
                positions_gained REAL,
                PRIMARY KEY (season, round, driver_id)
            )
        """)

        before = conn.execute(
            "SELECT COUNT(*) FROM race_results"
        ).fetchone()[0]

        columns = [
            "season", "round", "race_name", "race_date",
            "circuit_id", "country", "driver_id",
            "driver_name", "constructor_id",
            "constructor_name", "grid", "position",
            "points", "laps", "status", "race_time_ms",
            "fastest_lap_time", "finished",
            "positions_gained"
        ]

        records = df[columns].astype(object)
        records = records.where(pd.notna(records), None)

        placeholders = ", ".join(["?"] * len(columns))

        conn.executemany(
            f"""
            INSERT OR IGNORE INTO race_results
            ({", ".join(columns)})
            VALUES ({placeholders})
            """,
            records.itertuples(index=False, name=None)
        )

        conn.commit()

        after = conn.execute(
            "SELECT COUNT(*) FROM race_results"
        ).fetchone()[0]

        duplicates = conn.execute("""
            SELECT COUNT(*) FROM (
                SELECT season, round, driver_id
                FROM race_results
                GROUP BY season, round, driver_id
                HAVING COUNT(*) > 1
            )
        """).fetchone()[0]

        team_points = pd.read_sql_query("""
            SELECT constructor_name,
                   SUM(points) AS total_points
            FROM race_results
            GROUP BY constructor_name
            ORDER BY total_points DESC
        """, conn)

        print("Processed records:", len(df))
        print("Database records before:", before)
        print("New records inserted:", after - before)
        print("Database records after:", after)
        print("Duplicate records:", duplicates)

        print("\nPoints by constructor:")
        print(team_points.to_string(index=False))

        print("\nData count matches:", len(df) == after)
        print("Database saved: data/output.db")

    return after


if __name__ == "__main__":
    load_data()