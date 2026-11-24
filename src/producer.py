import json
from pathlib import Path

import pandas as pd
from kafka import KafkaProducer
from kafka.errors import KafkaError

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

TOPIC = "f1_race_results"
BOOTSTRAP_SERVER = "localhost:9092"


def produce_data():
    df = pd.read_csv(DATA_DIR / "raw_data.csv")

    records = json.loads(df.to_json(orient="records"))

    producer = None
    sent_count = 0

    try:
        producer = KafkaProducer(
            bootstrap_servers=BOOTSTRAP_SERVER,
            value_serializer=lambda value: json.dumps(
                value
            ).encode("utf-8"),
            key_serializer=lambda key: key.encode("utf-8"),
            acks="all",
            retries=3,
            request_timeout_ms=30000,
            max_block_ms=10000
        )

        print("Connected to Kafka.")
        print("Topic:", TOPIC)
        print("Records to send:", len(records))

        for record in records:
            key = (
                f"{record['season']}-"
                f"{record['round']}-"
                f"{record['driver_id']}"
            )

            future = producer.send(
                TOPIC,
                key=key,
                value=record
            )

            future.get(timeout=30)
            sent_count += 1

            if sent_count % 100 == 0:
                print("Sent records:", sent_count)

        producer.flush()

        print("\nKafka Producer completed.")
        print("Total sent records:", sent_count)

        return sent_count

    except KafkaError as error:
        print("Kafka error:", error)
        print("Successfully sent:", sent_count)
        raise

    finally:
        if producer is not None:
            producer.close()


if __name__ == "__main__":
    produce_data()