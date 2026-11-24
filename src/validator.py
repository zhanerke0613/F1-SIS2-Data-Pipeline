from pathlib import Path

import pandas as pd
import pandera.pandas as pa
from pandera import Check, Column, DataFrameSchema
from src.config import SEASON

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

schema = DataFrameSchema(
    {
        "season": Column(int, Check.equal_to(SEASON)),
        "round": Column(int, Check.in_range(1, 24)),
        "driver_id": Column(str, Check.str_length(min_value=1)),
        "constructor_id": Column(str, Check.str_length(min_value=1)),
        "points": Column(float, Check.in_range(0, 26)),
        "grid": Column(int, Check.in_range(0, 30)),
        "laps": Column(int, Check.ge(0)),
        "race_date": Column(
            pa.DateTime,
            Check.in_range(
                pd.Timestamp(f"{SEASON}-01-01"),
                pd.Timestamp(f"{SEASON}-12-31")
            )
        ),
        "is_test_record": Column(bool)
    },
    unique=["season", "round", "driver_id"],
    coerce=True
)


def validate_data(input_path=None):
    if input_path is None:
        input_path = DATA_DIR / "raw_data.csv"

    df = pd.read_csv(input_path)
    df["is_test_record"] = False

    # Create three invalid test records
    test_records = df.head(3).copy()
    test_records["is_test_record"] = True

    test_records["driver_id"] = [
        "test_driver_1",
        "test_driver_2",
        ""
    ]

    test_records.loc[test_records.index[0], "points"] = -10
    test_records.loc[test_records.index[1], "race_date"] = f"{SEASON + 1}-01-01"

    combined = pd.concat(
        [df, test_records],
        ignore_index=True
    )

    print("Original records:", len(df))
    print("Test records:", len(test_records))
    print("Total records:", len(combined))

    try:
        schema.validate(combined, lazy=True)
        invalid_indices = []

    except pa.errors.SchemaErrors as error:
        failures = error.failure_cases

        print("\nValidation errors:")
        print(failures.to_string(index=False))

        if failures["index"].isna().any():
            raise ValueError(
                "Dataset-level validation error"
            ) from error

        invalid_indices = (
            failures["index"]
            .astype(int)
            .unique()
            .tolist()
        )

        reasons = failures.groupby("index")["check"].agg(
            lambda values: "; ".join(
                dict.fromkeys(map(str, values))
            )
        )

        invalid = combined.loc[invalid_indices].copy()
        invalid["validation_error"] = invalid.index.map(reasons)

        invalid.to_csv(
            DATA_DIR / "invalid_records.csv",
            index=False
        )

    if not invalid_indices:
        pd.DataFrame(
            columns=list(combined.columns) + ["validation_error"]
        ).to_csv(
            DATA_DIR / "invalid_records.csv",
            index=False
        )

    valid = combined.drop(index=invalid_indices)
    valid = valid[~valid["is_test_record"]].copy()
    valid = valid.drop(columns=["is_test_record"])

    valid.to_csv(
        DATA_DIR / "valid_records.csv",
        index=False
    )

    print("\nValidation completed.")
    print("Valid records:", len(valid))
    print("Invalid records:", len(invalid_indices))
    print("Valid data saved to data/valid_records.csv")
    print("Invalid data saved to data/invalid_records.csv")

    return valid


if __name__ == "__main__":
    validate_data()