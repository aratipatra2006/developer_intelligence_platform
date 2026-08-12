import os
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
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


# 4. FEATURES

categorical_features = ["language"]

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


# 5. PREPROCESSING

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
        OneHotEncoder(handle_unknown="ignore")
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


# 6. TRAIN / TEST SPLIT

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))


# 7. MODELS

models = {

    "Linear Regression":
        LinearRegression(),

    "Decision Tree":
        DecisionTreeRegressor(
            random_state=42,
            max_depth=10
        ),

    "Random Forest":
        RandomForestRegressor(
            n_estimators=200,
            random_state=42,
            n_jobs=-1
        )
}


# 8. TRAIN AND EVALUATE

results = []


for name, model in models.items():

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

    # Train
    pipeline.fit(
        X_train,
        y_train
    )

    # Predictions
    train_predictions = pipeline.predict(X_train)
    test_predictions = pipeline.predict(X_test)

    # Training metrics

    train_mae = mean_absolute_error(
        y_train,
        train_predictions
    )

    train_rmse = mean_squared_error(
        y_train,
        train_predictions
    ) ** 0.5

    train_r2 = r2_score(
        y_train,
        train_predictions
    )

    # Testing metrics

    test_mae = mean_absolute_error(
        y_test,
        test_predictions
    )

    test_rmse = mean_squared_error(
        y_test,
        test_predictions
    ) ** 0.5

    test_r2 = r2_score(
        y_test,
        test_predictions
    )

    # R² gap

    r2_gap = train_r2 - test_r2

    # MAPE

    non_zero_mask = y_test != 0

    y_test_non_zero = y_test[non_zero_mask]

    predictions_non_zero = test_predictions[
        non_zero_mask
    ]

    mape = mean_absolute_percentage_error(
        y_test_non_zero,
        predictions_non_zero
    ) * 100

    prediction_accuracy = 100 - mape

    # Store results

    results.append({

        "Model": name,

        "Train R²": train_r2,

        "Test R²": test_r2,

        "R² Gap": r2_gap,

        "Test MAE": test_mae,

        "Test RMSE": test_rmse,

        "R² %": test_r2 * 100,

        "MAPE %": mape,

        "Accuracy %": prediction_accuracy

    })


# 9. RESULTS TABLE

results_df = pd.DataFrame(results)


# Sort by testing R²
results_df = results_df.sort_values(
    by="Test R²",
    ascending=False
)


# 10. ROUND VALUES

display_df = results_df.copy()

numeric_columns = [
    "Train R²",
    "Test R²",
    "R² Gap",
    "Test MAE",
    "Test RMSE",
    "R² %",
    "MAPE %",
    "Accuracy %"
]

display_df[numeric_columns] = (
    display_df[numeric_columns].round(4)
)


# 11. DISPLAY ONLY ONE TABLE

print("\n")
print("=" * 110)
print("MODEL COMPARISON")
print("=" * 110)

print(
    display_df.to_string(index=False)
)

print("=" * 110)


# 12. BEST MODEL

best_model = results_df.iloc[0]

print("\nBest Model:")
print(best_model["Model"])

print(
    f"Testing R²: "
    f"{best_model['Test R²']:.4f}"
)

print(
    f"Testing R² Percentage: "
    f"{best_model['R² %']:.2f}%"
)


# 13. SAVE RESULTS

os.makedirs(
    "ml/data",
    exist_ok=True
)

RESULT_PATH = "ml/data/model_comparison.csv"

results_df.to_csv(
    RESULT_PATH,
    index=False
)

print("\nResults saved to:")
print(RESULT_PATH)