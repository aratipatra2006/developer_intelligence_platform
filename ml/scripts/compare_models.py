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

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ============================================================
# 1. LOAD DATASET
# ============================================================

DATASET = "ml/data/repository_dataset_scored.csv"

df = pd.read_csv(DATASET)

print("Dataset shape:", df.shape)


# ============================================================
# 2. TARGET
# ============================================================

y = pd.to_numeric(
    df["health_score"],
    errors="coerce"
)

X = df.drop(
    columns=["health_score", "repository"]
).copy()


# ============================================================
# 3. CLEAN COMPLEXITY
# ============================================================

X["complexity_supported"] = (
    X["complexity"]
    .astype(str)
    .str.lower()
    .ne("not supported")
    .astype(int)
)


# ============================================================
# 4. CONVERT ALL NON-CATEGORICAL FEATURES TO NUMERIC
# ============================================================

categorical_features = [
    "language"
]

for column in X.columns:

    if column not in categorical_features:

        X[column] = pd.to_numeric(
            X[column],
            errors="coerce"
        )


# ============================================================
# 5. FEATURES
# ============================================================

numeric_features = [
    column
    for column in X.columns
    if column not in categorical_features
]


# ============================================================
# 6. PREPROCESSING
# ============================================================

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


# ============================================================
# 7. TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))


# ============================================================
# 8. MODELS
# ============================================================

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


# ============================================================
# 9. TRAIN AND EVALUATE
# ============================================================

results = []

for name, model in models.items():

    print("\n" + "=" * 60)
    print("Training:", name)

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

    pipeline.fit(
        X_train,
        y_train
    )

    predictions = pipeline.predict(
        X_test
    )

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    rmse = mean_squared_error(
        y_test,
        predictions
    ) ** 0.5

    r2 = r2_score(
        y_test,
        predictions
    )

    results.append({
        "Model": name,
        "MAE": mae,
        "RMSE": rmse,
        "R2": r2
    })

    print("MAE :", round(mae, 4))
    print("RMSE:", round(rmse, 4))
    print("R²  :", round(r2, 4))


# ============================================================
# 10. RESULTS
# ============================================================

results_df = pd.DataFrame(results)

results_df = results_df.sort_values(
    by="R2",
    ascending=False
)

print("\n")
print("=" * 60)
print("MODEL COMPARISON")
print("=" * 60)

print(
    results_df.to_string(
        index=False
    )
)


# ============================================================
# 11. SAVE RESULTS
# ============================================================

os.makedirs(
    "ml/data",
    exist_ok=True
)

results_df.to_csv(
    "ml/data/model_comparison.csv",
    index=False
)

print("\nResults saved to:")
print("ml/data/model_comparison.csv")