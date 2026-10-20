import os
from pathlib import Path

import pandas as pd
import psycopg
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT/ ".env")
def prepare_dataset():
    
    connection_settings = {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
        "dbname": os.getenv("DB_NAME", "food_delivery_db"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD"),
    }
    if not connection_settings["password"]:
        raise ValueError("DB_Password is missing from .env")
    query = """
        SELECT
            delivery_time_minutes,
            weather,
            traffic_density,
            vehicle_condition,
            order_type,
            vehicle_type,
            festival,
            city,
            restaurant_latitude,
            restaurant_longitude,
            delivery_location_latitude,
            delivery_location_longitude
        FROM staging.delivery_orders
        WHERE delivery_time_minutes IS NOT NULL
          AND delivery_time_minutes > 0
    """
    with psycopg.connect(**connection_settings) as conn:
        df = pd.read_sql_query(query, conn)
    df['is_late'] =(
        df['delivery_time_minutes'] > 30
    ).astype(int)

    X = df.drop(
        columns=["delivery_time_minutes","is_late"]
    )
    y = df["is_late"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )
    output_dir = PROJECT_ROOT / "data" / "processed" / "ml"
    output_dir.mkdir(parents=True, exist_ok=True)

    X_train.to_csv(output_dir / "X_train.csv", index=False)
    X_test.to_csv(output_dir / "X_test.csv", index=False)
    y_train.to_csv(output_dir / "y_train.csv", index=False)
    y_test.to_csv(output_dir / "y_test.csv", index=False)

    print(f"Total eligible records: {len(df):,}")
    print(f"Training records: {len(X_train):,}")
    print(f"Testing records: {len(X_test):,}")
    print(f"Late-delivery rate: {y.mean():.2%}")
    print(f"Features: {list(X.columns)}")
    print(f"Saved dataset splits to: {output_dir}")

    
if __name__ == "__main__":
    prepare_dataset()