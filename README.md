# F1-SIS2-Data-Pipeline
Data Streaming and Validation Pipeline with Apache Kafka and Pandera.

# F1 2024 Data Pipeline — SIS 2

## Project Overview

This project implements an end-to-end data pipeline for
Formula 1 race results from the 2024 season.

The pipeline collects, transfers, validates, cleans,
stores and analyzes data automatically.

## Technologies

- Python 3.9
- REST API
- Apache Kafka
- Docker
- Pandera
- Pandas
- NumPy
- SQLite
- Matplotlib

## Data Source

Jolpica F1 API:
https://api.jolpi.ca/ergast/f1/2024/results.json

The dataset contains:

- 479 race results
- 24 races
- 24 drivers
- 10 constructors
- 17 original columns
- 19 processed columns

## Pipeline Architecture

API → Kafka Producer → Kafka Broker → Kafka Consumer
→ Pandera Validation → Data Cleaning → SQLite → EDA

## Project Structure

```text
F1-SIS2-Data-Pipeline/
├── src/
│   ├── api_client.py
│   ├── producer.py
│   ├── consumer.py
│   ├── validator.py
│   ├── cleaner.py
│   ├── loader.py
│   └── analysis.py
├── data/
├── figures/
├── docs/
│   └── data_dictionary.md
├── report/
├── main.py
├── requirements.txt
└── README.md
```

## Installation

Clone the repository:

```bash
git clone https://github.com/zhanerke0613/F1-SIS2-Data-Pipeline.git
cd F1-SIS2-Data-Pipeline
```

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Start Kafka

Make sure Docker is running.

```bash
docker pull apache/kafka:3.9.0
docker run -d --name kafka -p 127.0.0.1:9092:9092 apache/kafka:3.9.0
```

If the container already exists:

```bash
docker start kafka
```

Create the Kafka topic:

```bash
docker exec kafka /opt/kafka/bin/kafka-topics.sh --create --topic f1_race_results --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

Before repeating the full pipeline, delete and recreate
the local project topic to avoid reading old messages.

```bash
docker exec kafka /opt/kafka/bin/kafka-topics.sh --delete --topic f1_race_results --bootstrap-server localhost:9092
```

Wait until the topic is deleted, then recreate it using
the creation command above.

## Run the Pipeline

```bash
python main.py
```

## Expected Results

| Stage | Records |
|---|---:|
| API Collection | 479 |
| Kafka Producer | 479 |
| Kafka Consumer | 479 |
| Valid Records | 479 |
| Invalid Test Records | 3 |
| Processed Records | 479 |
| SQLite Records | 479 |
| Database Duplicates | 0 |

## Data Validation

Pandera validates data types, numerical ranges,
required fields, race dates and composite key uniqueness.

Three intentionally invalid records are used to test
the validation process. All three are detected and
excluded from the final dataset.

## Data Cleaning

- Duplicate removal
- Data type conversion
- Text normalization
- Missing value handling
- NumPy transformations
- Multi-condition filtering
- GroupBy aggregation
- Pivot table creation

## Database

The processed data is stored in data/output.db.

Table: race_results

Composite primary key: season, round, driver_id.

INSERT OR IGNORE prevents duplicate records.

The database is designed for a fixed historical dataset.
Existing records are not automatically updated.

## Exploratory Data Analysis

Three visualizations are generated:

1. Total race points by constructor
2. Starting grid vs finishing position
3. Race completion rate by constructor

Charts are saved in the figures/ directory.

## Key Findings

- McLaren earned the highest race points: 609.
- Ferrari earned 595 race points.
- The overall race completion rate was 88.73%.
- McLaren achieved a 100% completion rate.
- No duplicate records were found in SQLite.

Sprint race points are not included.

## Testing

- API collection test: Passed
- Kafka record transfer test: Passed
- Pandera invalid records test: Passed
- Database idempotency test: Passed
- End-to-end pipeline test: Passed

## Conclusion

The project demonstrates a complete automated data
pipeline using API collection, Kafka, data validation,
data cleaning, database storage and data analysis.