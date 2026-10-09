import json
from pathlib import Path

def load_json(file_path: str):
    
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File Not Found:{path}")

    with path.open("r",encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data,list):
        raise ValueError("Expected the JSON root to be a list of record")

    return data

if __name__ == '__main__':
    file_path ="data/raw/India-Food-Delivery-Time-Prediction.txt"


    records = load_json(file_path)
    print(f"Root Type: {type(records).__name__}")

    print(f"Number of Records: {len(records)}")

    if records:
        print(f"Number of fields: {len(records[0])}")
        print("Fields:")
        for field in records[0].keys():
            print(f" -{field}")