import os
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    mean_absolute_percentage_error
)


# 1. LOAD DATASET

DATASET = "ml/data/repository_dataset_scored.csv"

df = pd.read_csv(DATASET)

print("Dataset shape:", df.shape)


# 2. TARGET AND FEATURES

y = pd.to_numeric(
    df["health_score"],
    errors="coerce"
)

X = df.drop(
    columns=["health_score", "repository"]
).copy()


# 3. CLEAN COMPLEXITY

X["complexity_supported"] = (
    X["complexity"]
    .astype(str)
    .str.lower()
    .ne("not supported")
    .astype(int)
)


# 4. CATEGORICAL FEATURES

categorical_features = [
    "language"
]


# 5. CONVERT NUMERIC FEATURES

for column in X.columns:

    if column not in categorical_features:

        X[column] = pd.to_numeric(
            X[column],
            errors="coerce"
        )


numeric_features = [
    column
    for column in X.columns
    if column not in categorical_features
]


# 6. PREPROCESSING

numeric_pipeline = Pipeline([
    (
        "imputer",
        SimpleImputer(strategy="median")
    )
])


categorical_pipeline = Pipeline([
    (
        "imputer",
        SimpleImputer(strategy="most_frequent")
    ),
    (
        "encoder",
        OneHotEncoder(
            handle_unknown="ignore"
        )
    )
])


preprocessor = ColumnTransformer([
    (
        "numeric",
        numeric_pipeline,
        numeric_features
    ),
    (
        "categorical",
        categorical_pipeline,
        categorical_features
    )
])


# 7. TRAIN / TEST SPLIT

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))


# 8. RANDOM FOREST REGRESSOR

model = RandomForestRegressor(
    n_estimators=200,
    random_state=42,
    n_jobs=-1
)


pipeline = Pipeline([
    (
        "preprocessor",
        preprocessor
    ),
    (
        "model",
        model
    )
])


# 9. TRAIN MODEL

print("\nTraining final Random Forest...")

pipeline.fit(
    X_train,
    y_train
)

print("Training completed.")


# 10. PREDICTIONS

predictions = pipeline.predict(
    X_test
)


# 11. EVALUATION METRICS

# Mean Absolute Error
mae = mean_absolute_error(
    y_test,
    predictions
)


# Root Mean Squared Error
rmse = mean_squared_error(
    y_test,
    predictions
) ** 0.5


# R² Score
r2 = r2_score(
    y_test,
    predictions
)


# 12. MAPE AND PERCENTAGE ACCURACY

# MAPE has a problem when actual values are zero.
# Therefore, only non-zero actual health scores are used.

non_zero_mask = y_test != 0

y_test_non_zero = y_test[non_zero_mask]
predictions_non_zero = predictions[non_zero_mask]


if len(y_test_non_zero) > 0:

    mape = mean_absolute_percentage_error(
        y_test_non_zero,
        predictions_non_zero
    )

    mape_percentage = mape * 100

    percentage_accuracy = 100 - mape_percentage

else:

    mape_percentage = None
    percentage_accuracy = None


# 13. DISPLAY FINAL RESULTS

print("\n" + "=" * 60)
print("FINAL RANDOM FOREST PERFORMANCE")
print("=" * 60)

print(f"MAE                 : {mae:.4f}")
print(f"RMSE                : {rmse:.4f}")
print(f"R² Score            : {r2:.4f}")
print(f"R² Percentage       : {r2 * 100:.2f}%")


if percentage_accuracy is not None:

    print(f"MAPE                : {mape_percentage:.2f}%")
    print(
        f"Prediction Accuracy : {percentage_accuracy:.2f}%"
    )

else:

    print("MAPE                : Cannot calculate")
    print("Prediction Accuracy : Cannot calculate")


print("=" * 60)


# 14. TRAINING VS TESTING R²

train_predictions = pipeline.predict(
    X_train
)

train_r2 = r2_score(
    y_train,
    train_predictions
)


print("\n" + "=" * 60)
print("TRAINING VS TESTING PERFORMANCE")
print("=" * 60)

print(f"Training R² : {train_r2:.4f}")
print(f"Testing R²  : {r2:.4f}")

print("=" * 60)


# 15. SAVE MODEL

os.makedirs(
    "ml/models",
    exist_ok=True
)


MODEL_PATH = "ml/models/repository_health_model.pkl"


joblib.dump(
    pipeline,
    MODEL_PATH
)


print("\nFinal model saved to:")
print(MODEL_PATH)