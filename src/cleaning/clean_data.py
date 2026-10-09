import pandas as pd
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.ingestion.json_loader import load_json

records = load_json("data/raw/India-Food-Delivery-Time-Prediction.txt")
df = pd.DataFrame(records)

numeric_columns=[
    "Delivery_person_Age",
    "Delivery_person_Ratings",
    "multiple_deliveries",
    "Time_taken(min)"
]
for column in numeric_columns:
    df[column]=(
        df[column].astype(str).str.replace("(min)","",regex=False).str.strip()
    )
    df[column] = pd.to_numeric(df[column],errors="coerce")
    # print(df[numeric_columns].dtypes)
    # print(df[numeric_columns].isna().sum())
    # print(df[numeric_columns].head())
    # print(df[numeric_columns].isna().sum())

# print("\nAge:")
# print(df[df["Delivery_person_Age"].isna()]["Delivery_person_ID"].head())

# print("\nRatings:")
# print(df[df["Delivery_person_Ratings"].isna()]["Delivery_person_ID"].head())

# print("\nMultiple deliveries:")
# print(df[df["multiple_deliveries"].isna()]["Delivery_person_ID"].head())

# age_missing = df[df["Delivery_person_Age"].isna()]

# print("Unique delivery persons with missing age:",
#       age_missing["Delivery_person_ID"].nunique())

# print("\nMost frequent delivery persons:")
# print(age_missing["Delivery_person_ID"].value_counts().head(10))


# ratings_missing = df[df["Delivery_person_Ratings"].isna()]

# print("Unique delivery persons with missing ratings:",
#       ratings_missing["Delivery_person_ID"].nunique())

# print("\nMost frequent delivery persons:")
# print(ratings_missing["Delivery_person_ID"].value_counts().head(10))

# print(
#     df[["Delivery_person_Age", "Delivery_person_Ratings"]]
#     .isna()
#     .value_counts()
# )

# print(df["multiple_deliveries"].value_counts(dropna=False))
# missing_multiple = df[df["multiple_deliveries"].isna()]

# print("Missing rows:", len(missing_multiple))
# print("Unique delivery persons:",
#       missing_multiple["Delivery_person_ID"].nunique())

# print("\nCity:")
# print(missing_multiple["City"].value_counts(dropna=False))

# print("\nTime taken:")
# print(missing_multiple["Time_taken(min)"].describe())

df["multiple_deliveries_missing"] = df["multiple_deliveries"].isna().astype(int)

print(df["Delivery_person_Age"].describe())
print()
print(df["Delivery_person_Ratings"].describe())

print("Age missing:", df["Delivery_person_Age"].isna().sum())
print("Ratings missing:", df["Delivery_person_Ratings"].isna().sum())