from pathlib import Path

import pandas as pd

from src.config import SEASON
from src.api_client import collect_data
from src.producer import produce_data
from src.consumer import consume_data
from src.validator import validate_data
from src.cleaner import clean_data
from src.loader import load_data
from src.analysis import analyze_data

DATA_DIR = Path(__file__).resolve().parent / "data"


def main():
    print("=" * 50)
    print(f"F1 {SEASON} DATA PIPELINE")
    print("=" * 50)

    print("\nSTEP 1: API Data Collection")
    raw = collect_data()

    print("\nSTEP 2: Kafka Producer")
    sent = produce_data()

    print("\nSTEP 3: Kafka Consumer")
    received = consume_data(expected_count=sent)

    # Verify Kafka data against the source
    consumed = pd.read_csv(
        DATA_DIR / "consumed_records.csv"
    )

    source = pd.read_csv(DATA_DIR / "raw_data.csv")
    keys = ["season", "round", "driver_id"]

    pd.testing.assert_frame_equal(
        source.sort_values(keys).reset_index(drop=True),
        consumed.sort_values(keys).reset_index(drop=True),
        check_dtype=False
    )

    print("\nSTEP 4: Pandera Validation")
    valid = validate_data(
        DATA_DIR / "consumed_records.csv"
    )

    print("\nSTEP 5: Data Cleaning")
    processed = clean_data()

    print("\nSTEP 6: SQLite Database")
    stored = load_data()

    print("\nIDEMPOTENCY TEST: Second Database Load")
    stored_again = load_data()

    if stored_again != stored:
        raise RuntimeError("Database idempotency test failed.")

    invalid_count = len(pd.read_csv(
        DATA_DIR / "invalid_records.csv"
    ))

    print("\nSTEP 7: Exploratory Data Analysis")
    analyze_data()

    if not len(raw) == sent == received:
        raise RuntimeError("Kafka record count mismatch.")

    if len(processed) != stored:
        raise RuntimeError("Database record count mismatch.")

    print("\n" + "=" * 50)
    print("PIPELINE SUMMARY")
    print("=" * 50)

    print("API records:", len(raw))
    print("Kafka sent:", sent)
    print("Kafka received:", received)
    print("Valid records:", len(valid))
    print("Invalid records:", invalid_count)
    print("Idempotency test: PASSED")
    print("Processed records:", len(processed))
    print("Database records:", stored)
    print("Charts generated: 3")

    print("\nPipeline completed successfully!")


if __name__ == "__main__":
    main()