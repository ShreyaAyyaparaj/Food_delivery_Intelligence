from pathlib import Path

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer #applies different preprocessing to different columns
from sklearn.dummy import DummyClassifier #Creates a simple baseline to compare against our model.
from sklearn.impute import SimpleImputer #Fills missing feature values.
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline #Connects preprocessing and modelling into one workflow.
from sklearn.preprocessing import OneHotEncoder, StandardScaler #Converts categorical values into numerical columns.


# 1. Locate the prepared datasets.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "processed" / "ml"
MODEL_DIR = PROJECT_ROOT / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def train_model():
    print("Training function started!", flush=True)
    # 2. Load the training and testing datasets.
    X_train = pd.read_csv(DATA_DIR / "X_train.csv")
    X_test = pd.read_csv(DATA_DIR / "X_test.csv")
    y_train = pd.read_csv(DATA_DIR / "y_train.csv")["is_late"]
    y_test = pd.read_csv(DATA_DIR / "y_test.csv")["is_late"]

    # 3. Identify numerical and categorical features.
    numeric_features = X_train.select_dtypes(
        include=["number"]
    ).columns.tolist()

    categorical_features = X_train.select_dtypes(
        exclude=["number"]
    ).columns.tolist()

    # 4. Handle missing numerical values and scale them.
    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    # 5. Handle missing categories and encode text as numbers.
    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore")),
    ])

    # 6. Apply the appropriate preprocessing to each column type.
    preprocessor = ColumnTransformer([
        ("numeric", numeric_pipeline, numeric_features),
        ("categorical", categorical_pipeline, categorical_features),
    ])

    # 7. Build the complete ML pipeline.
    model = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", LogisticRegression(max_iter=1000)),
    ])

    
    # 8. Create a validation set from the training data.
    X_fit, X_val, y_fit, y_val = train_test_split(
        X_train,
        y_train,
        test_size=0.20,
        random_state=42,
        stratify=y_train,
    )

    # 9. Train using only the smaller fitting subset.
    model.fit(X_fit, y_fit)

    # 10. Get validation probabilities.
    val_probabilities = model.predict_proba(X_val)[:, 1]

    # 11. Compare different classification thresholds.
    from sklearn.metrics import precision_score, recall_score, f1_score

    thresholds = [0.30, 0.35, 0.40, 0.45, 0.50]
    best_threshold = 0.50
    best_f1 = -1

    print("\n--- Validation Threshold Comparison ---")

    for threshold in thresholds:
        val_predictions = (
            val_probabilities >= threshold
        ).astype(int)

        precision = precision_score(
            y_val, val_predictions, zero_division=0
        )
        recall = recall_score(
            y_val, val_predictions, zero_division=0
        )
        f1 = f1_score(
            y_val, val_predictions, zero_division=0
        )

        print(
            f"Threshold={threshold:.2f} | "
            f"Precision={precision:.3f} | "
            f"Recall={recall:.3f} | "
            f"F1={f1:.3f}"
        )
        
        if f1 > best_f1:
            best_f1 = f1
            best_threshold = threshold

    print(f"\nSelected threshold: {best_threshold:.2f}")

    # 12. Retrain on all training records.
    model.fit(X_train, y_train)

    # 13. Evaluate once on the untouched test set.
    test_probabilities = model.predict_proba(X_test)[:, 1]
    test_predictions = (
        test_probabilities >= best_threshold
    ).astype(int)

    print("\n--- Final Test Results ---")
    print(f"Threshold: {best_threshold:.2f}")
    print(f"Accuracy: {accuracy_score(y_test, test_predictions):.4f}")
    print(f"ROC-AUC: {roc_auc_score(y_test, test_probabilities):.4f}")
    print(
        classification_report(
            y_test, test_predictions, zero_division=0
        )
    )
    print("Confusion matrix:")
    print(confusion_matrix(y_test, test_predictions))

    # 14. Save the trained model.
    model_path = MODEL_DIR / "late_delivery_logistic_regression.joblib"
    joblib.dump(model, model_path)
    print(f"\nSaved model to: {model_path}")

    # Save the selected threshold for later prediction use.
    threshold_path = MODEL_DIR / "late_delivery_threshold.txt"
    threshold_path.write_text(str(best_threshold), encoding="utf-8")
    print(f"Saved threshold to: {threshold_path}")

if __name__ == "__main__":
    train_model()