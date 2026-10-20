import os
from pathlib import Path

import pandas as pd
import psycopg
from dotenv import load_dotenv

# Load database credentials from the project-root .env file
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

CSV_PATH = PROJECT_ROOT / "data" / "processed" / "food_delivery_clean.csv"

COLUMN_MAP = {
    "ID": "order_id",
    "Delivery_person_ID": "delivery_person_id",
    "Delivery_person_Age": "delivery_person_age",
    "Delivery_person_Ratings": "delivery_person_ratings",
    "Restaurant_latitude": "restaurant_latitude",
    "Restaurant_longitude": "restaurant_longitude",
    "Delivery_location_latitude": "delivery_location_latitude",
    "Delivery_location_longitude": "delivery_location_longitude",
    "Order_Date": "order_date",
    "Time_Orderd": "order_time",
    "Time_Order_picked": "pickup_time",
    "Weatherconditions": "weather",
    "Road_traffic_density": "traffic_density",
    "Vehicle_condition": "vehicle_condition",
    "Type_of_order": "order_type",
    "Type_of_vehicle": "vehicle_type",
    "multiple_deliveries": "multiple_deliveries",
    "Festival": "festival",
    "City": "city",
    "Time_taken(min)": "delivery_time_minutes",
    "order_datetime": "order_datetime",
    "pickup_datetime": "pickup_datetime",
}

NUMERIC_COLUMNS = [
    "Delivery_person_Age",
    "Delivery_person_Ratings",
    "Restaurant_latitude",
    "Restaurant_longitude",
    "Delivery_location_latitude",
    "Delivery_location_longitude",
    "Vehicle_condition",
    "multiple_deliveries",
    "Time_taken(min)",
]

DATE_COLUMNS = ["Order_Date"]
TIME_COLUMNS = ["Time_Orderd", "Time_Order_picked"]
TIMESTAMP_COLUMNS = ["order_datetime", "pickup_datetime"]


def load_to_postgres():
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV not found: {CSV_PATH}")

    df = pd.read_csv(CSV_PATH)

    # Convert numeric fields explicitly
    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # Convert dates, times, and timestamps to database-compatible values
    for column in DATE_COLUMNS:
        df[column] = pd.to_datetime(
            df[column], errors="coerce"
        ).dt.date

    for column in TIME_COLUMNS:
        parsed = pd.to_datetime(df[column], errors="coerce")
        df[column] = parsed.dt.time

    for column in TIMESTAMP_COLUMNS:
        df[column] = pd.to_datetime(
            df[column], errors="coerce"
        )

    # Rename CSV fields to match PostgreSQL column names
    df = df.rename(columns=COLUMN_MAP)

    # Convert pandas missing values to Python None -> SQL NULL
    df = df.astype(object).where(pd.notna(df), None)

    columns = list(COLUMN_MAP.values())
    placeholders = ", ".join(["%s"] * len(columns))
    column_sql = ", ".join(f'"{col}"' for col in columns)

    insert_sql = f"""
        INSERT INTO staging.delivery_orders ({column_sql})
        VALUES ({placeholders})
    """

    connection_settings = {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
        "dbname": os.getenv("DB_NAME", "food_delivery_db"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD"),
    }

    if not connection_settings["password"]:
        raise ValueError("DB_PASSWORD is missing from .env")

    records = list(df[columns].itertuples(index=False, name=None))

    # One transaction: failed loads roll back, including the truncate
    with psycopg.connect(**connection_settings) as conn:
        with conn.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE staging.delivery_orders")

            batch_size = 1000
            for start in range(0, len(records), batch_size):
                cursor.executemany(
                    insert_sql,
                    records[start:start + batch_size],
                )

    print(f"Loaded {len(records):,} records into staging.delivery_orders")


if __name__ == "__main__":
    load_to_postgres()
