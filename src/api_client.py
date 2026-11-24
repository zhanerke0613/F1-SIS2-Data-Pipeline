import requests
import time
import pandas as pd
from pathlib import Path

URL = "https://api.jolpi.ca/ergast/f1/2024/results.json"


def fetch_page(params):
    for attempt in range(3):
        try:
            response = requests.get(
                URL, params=params, timeout=30
            )

            if response.status_code == 429:
                print("Rate limit exceeded.")

                if attempt == 2:
                    response.raise_for_status()

                time.sleep(60)
                continue

            response.raise_for_status()
            return response.json()["MRData"]

        except requests.exceptions.Timeout:
            print("Error: Request timed out.")
            raise

        except requests.exceptions.ConnectionError:
            print("Error: Connection failed.")
            raise

        except requests.exceptions.HTTPError as error:
            print("HTTP Error:", error)
            raise

        except requests.exceptions.RequestException as error:
            print("Request Error:", error)
            raise


def collect_data():
    limit = 30
    offset = 0
    records = []

    while True:
        params = {
            "limit": limit,
            "offset": offset
        }

        data = fetch_page(params)
        total = int(data["total"])
        races = data["RaceTable"]["Races"]
        page_records = []

        for race in races:
            for result in race["Results"]:
                record = {
                    "season": race["season"],
                    "round": race["round"],
                    "race_name": race["raceName"],
                    "race_date": race["date"],
                    "circuit_id": race["Circuit"]["circuitId"],
                    "country": race["Circuit"]["Location"]["country"],
                    "driver_id": result["Driver"]["driverId"],
                    "driver_name": result["Driver"]["givenName"] + " " + result["Driver"]["familyName"],
                    "constructor_id": result["Constructor"]["constructorId"],
                    "constructor_name": result["Constructor"]["name"],
                    "grid": result["grid"],
                    "position": result["position"],
                    "points": result["points"],
                    "laps": result["laps"],
                    "status": result["status"],
                    "race_time_ms": result.get("Time", {}).get("millis"),
                    "fastest_lap_time": result.get("FastestLap", {}).get("Time", {}).get("time")
                }

                page_records.append(record)

        if not page_records:
            break

        records.extend(page_records)

        print(f"Offset: {offset} | Collected: {len(records)}")

        offset += len(page_records)

        if offset >= total:
            break

        time.sleep(0.5)

    if len(records) != total:
        raise RuntimeError("Incomplete data collection.")

    df = pd.DataFrame(records)

    output_path = Path(__file__).resolve().parent.parent / "data" / "raw_data.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(output_path, index=False)

    print("\nAPI collection completed.")
    print("Total collected records:", len(records))
    print("Dataset shape:", df.shape)
    print("Data saved to data/raw_data.csv")

    return df


if __name__ == "__main__":
    collect_data()