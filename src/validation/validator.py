import pandas as pd

REQUIRED_COLUMNS = [
    "ID",
    "Delivery_person_ID",
    "Delivery_person_Age",
    "Delivery_person_Ratings",
    "Restaurant_latitude",
    "Restaurant_longitude",
    "Delivery_location_latitude",
    "Delivery_location_longitude",
    "Order_Date",
    "Time_Orderd",
    "Time_Order_picked",
    "Weatherconditions",
    "Road_traffic_density",
    "Vehicle_condition",
    "Type_of_order",
    "Type_of_vehicle",
    "multiple_deliveries",
    "Festival",
    "City",
    "Time_taken(min)"
]

def validate_schema(df):
    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]
    unexpected_columns = [
        column for column in df.columns
        if column not in REQUIRED_COLUMNS
    ]

    return {
        "missing_columns": missing_columns,
        "unexpected_columns": unexpected_columns,
        "schema_valid": len(missing_columns) == 0,
    }


def check_duplicates(df):
    return {
        "duplicated_rows": int(df.duplicated().sum()),
        "duplicated_ids": int(df["ID"].duplicated().sum()),
    }


def check_missing_values(df):
    return df.isna().sum().to_dict()

def investigate_missing_time(df):
    missing = df[df["Time_Orderd"].isna()]

    print("Missing Time_Ordered records:", len(missing))
    print("\n Time_Order_picked values:")
    print(missing["Time_Order_picked"].value_counts().head(10))

    print("\nTarget distribution:")
    print(missing["Time_taken(min)"].describe())
    
    print("\nWeatherconditions:")
    print(missing["Weatherconditions"].value_counts().head())

    print("\nCity:")
    print(missing["City"].value_counts())

    print("\nTraffic density:")
    print(missing["Road_traffic_density"].value_counts())
    
if __name__ == '__main__':
    from pathlib import Path
    import sys

    sys.path.append(str(Path(__file__).resolve().parents[2]))

    from src.ingestion.json_loader import load_json

    records = load_json("data/raw/India-Food-Delivery-Time-Prediction.txt")

    df = pd.DataFrame(records)

    # print("===SCHEMA===")
    # print(validate_schema(df))

    # print("\n=== DUPLICATES ====")
    # print(check_duplicates(df))

    # print("\n=== MISSING VALUES ===")
    # print(check_missing_values(df))

    print(investigate_missing_time(df))
    