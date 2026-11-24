import json
from pathlib import Path

import pandas as pd
from kafka import KafkaConsumer
from kafka.errors import KafkaError

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

TOPIC = "f1_race_results"
BOOTSTRAP_SERVER = "localhost:9092"


def consume_data(expected_count=None):
    raw = pd.read_csv(DATA_DIR / "raw_data.csv")

    if expected_count is None:
        expected_count = len(raw)

    columns = raw.columns.tolist()

    consumer = None
    records = {}
    skipped = 0
    duplicates = 0

    try:
        consumer = KafkaConsumer(
            TOPIC,
            bootstrap_servers=BOOTSTRAP_SERVER,
            auto_offset_reset="earliest",
            enable_auto_commit=False,
            group_id=None,
            consumer_timeout_ms=10000
        )

        print("Connected to Kafka.")
        print("Topic:", TOPIC)
        print("Expected records:", expected_count)

        for message in consumer:
            try:
                record = json.loads(
                    message.value.decode("utf-8")
                )

                if not isinstance(record, dict):
                    skipped += 1
                    continue

                # Skip test messages and incomplete records
                if not all(col in record for col in columns):
                    skipped += 1
                    continue

                key = (
                    record["season"],
                    record["round"],
                    record["driver_id"]
                )

                if key in records:
                    duplicates += 1

                records[key] = record

                if len(records) % 100 == 0:
                    print("Received records:", len(records))

                if len(records) >= expected_count:
                    break

            except (json.JSONDecodeError, UnicodeDecodeError):
                skipped += 1
                print("Invalid JSON message skipped.")

        df = pd.DataFrame(
            list(records.values()),
            columns=columns
        )

        df.to_csv(
            DATA_DIR / "consumed_records.csv",
            index=False
        )

        print("\nKafka Consumer completed.")
        print("Total received records:", len(df))
        print("Skipped messages:", skipped)
        print("Duplicate messages:", duplicates)
        print("Record count matches:", len(df) == expected_count)
        print("Saved: data/consumed_records.csv")

        if len(df) != expected_count:
            raise RuntimeError("Incomplete Kafka consumption.")

        return len(df)

    except KafkaError as error:
        print("Kafka connection error:", error)
        raise

    finally:
        if consumer is not None:
            consumer.close()


if __name__ == "__main__":
    consume_data()