import os
import joblib
import pandas as pd


MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "models",
    "repository_health_model.pkl"
)

model = joblib.load(MODEL_PATH)


def predict_health_score(repository_data):
    """
    Predict repository health score using the trained Random Forest model.
    """

    df = pd.DataFrame([repository_data])

    # Same feature engineering used during training
    df["complexity_supported"] = (
        df["complexity"]
        .astype(str)
        .str.lower()
        .ne("not supported")
        .astype(int)
    )

    df["complexity"] = pd.to_numeric(
        df["complexity"],
        errors="coerce"
    )

    categorical_features = ["language"]

    for column in df.columns:
        if column not in categorical_features:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    prediction = model.predict(df)[0]

    return float(prediction)