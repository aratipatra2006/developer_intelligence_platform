"""
Repository Health Classification Model

Predicts repository health category from repository-analysis features.

Target:
    health_grade

Classes:
    Excellent
    Good
    Moderate
    Needs Improvement
    Poor

Models:
    1. Logistic Regression
    2. Decision Tree Classifier
    3. Random Forest Classifier
    4. Voting Classifier

Evaluation:
    - 80/20 stratified train-test split
    - Accuracy
    - Precision
    - Recall
    - F1-score
    - Stratified cross-validation

Important:
    health_grade is currently generated from deterministic health-score rules.
    Therefore, this classifier learns to reproduce those labels rather than
    independently verified software quality.
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer

from sklearn.ensemble import (
    RandomForestClassifier,
    VotingClassifier,
)

from sklearn.impute import SimpleImputer

from sklearn.linear_model import LogisticRegression

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
)

from sklearn.model_selection import (
    StratifiedKFold,
    cross_val_score,
    train_test_split,
)

from sklearn.pipeline import Pipeline

from sklearn.preprocessing import (
    OneHotEncoder,
    StandardScaler,
)

from sklearn.tree import DecisionTreeClassifier


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

DATA_FILE = (
    ROOT
    / "ml"
    / "data"
    / "repository_dataset.csv"
)

MODEL_FILE = (
    ROOT
    / "ml"
    / "health_model.pkl"
)

METRICS_FILE = (
    ROOT
    / "ml"
    / "health_model_metrics.json"
)

FEATURE_FILE = (
    ROOT
    / "ml"
    / "health_model_features.json"
)


# ============================================================
# CONFIGURATION
# ============================================================

TARGET = "health_grade"

TEST_SIZE = 0.20

RANDOM_STATE = 42


# ============================================================
# FEATURES TO EXCLUDE
# ============================================================

# These columns must not be given to the model.
EXCLUDED_FEATURES = {
    "repository",
    "health_score",
    "health_grade",
}


# Popularity metrics are not used for health classification.
EXCLUDED_FEATURES.update(
    {
        "stars",
        "forks",
        "watchers",
        "open_issues",
    }
)


CATEGORICAL_FEATURES = {
    "language",
}


# ============================================================
# LOAD DATASET
# ============================================================

def load_dataset() -> pd.DataFrame:
    """Load and validate the repository dataset."""

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found:\n{DATA_FILE}"
        )

    df = pd.read_csv(
        DATA_FILE
    )

    if TARGET not in df.columns:
        raise ValueError(
            f"Missing target column: {TARGET}"
        )

    # --------------------------------------------------------
    # Convert unsupported numeric values to NaN.
    #
    # Examples:
    #     "-"
    #     "Not Supported"
    #
    # The numeric imputer will handle these later.
    # --------------------------------------------------------

    numeric_columns = [
        "total_files",
        "total_folders",
        "lines",
        "python",
        "html",
        "css",
        "javascript",
        "java",
        "cpp",
        "dependency_count",
        "readme_score",
        "functions",
        "complexity",
        "language_count",
        "tech_stack_count",
        "size",
        "created_days",
        "updated_days",
        "complexity_supported",
        "functions_supported",
    ]

    for column in numeric_columns:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            )

    # --------------------------------------------------------
    # Remove rows without a target.
    # --------------------------------------------------------

    df = df.dropna(
        subset=[TARGET]
    ).reset_index(drop=True)

    if len(df) < 50:
        raise ValueError(
            f"Only {len(df)} usable rows available. "
            "More training data is recommended."
        )

    return df


# ============================================================
# FEATURE COLUMNS
# ============================================================

def get_feature_columns(
    df: pd.DataFrame,
) -> list[str]:
    """Return columns used as model inputs."""

    return [
        column
        for column in df.columns
        if column not in EXCLUDED_FEATURES
    ]


# ============================================================
# COLUMN TYPES
# ============================================================

def get_column_types(
    X: pd.DataFrame,
) -> tuple[list[str], list[str]]:
    """Separate numerical and categorical features."""

    categorical_features = [
        column
        for column in CATEGORICAL_FEATURES
        if column in X.columns
    ]

    numerical_features = [
        column
        for column in X.columns
        if column not in categorical_features
    ]

    return (
        numerical_features,
        categorical_features,
    )


# ============================================================
# STANDARD PREPROCESSOR
# ============================================================

def build_preprocessor(
    X: pd.DataFrame,
) -> ColumnTransformer:
    """
    Preprocessor for tree-based models.

    Numerical:
        Missing values → median

    Categorical:
        Missing values → most frequent
        Categories → one-hot encoding
    """

    numerical_features, categorical_features = (
        get_column_types(X)
    )

    numerical_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="median"
                ),
            )
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="most_frequent"
                ),
            ),
            (
                "onehot",
                OneHotEncoder(
                    handle_unknown="ignore"
                ),
            ),
        ]
    )

    return ColumnTransformer(
        transformers=[
            (
                "numeric",
                numerical_pipeline,
                numerical_features,
            ),
            (
                "categorical",
                categorical_pipeline,
                categorical_features,
            ),
        ]
    )


# ============================================================
# SCALED PREPROCESSOR
# ============================================================

def build_scaled_preprocessor(
    X: pd.DataFrame,
) -> ColumnTransformer:
    """
    Preprocessor for Logistic Regression.

    Numerical:
        Missing values → median
        Values → StandardScaler

    Scaling is important because repository features have
    very different ranges.
    """

    numerical_features, categorical_features = (
        get_column_types(X)
    )

    numerical_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="median"
                ),
            ),
            (
                "scaler",
                StandardScaler()
            ),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="most_frequent"
                ),
            ),
            (
                "onehot",
                OneHotEncoder(
                    handle_unknown="ignore"
                ),
            ),
        ]
    )

    return ColumnTransformer(
        transformers=[
            (
                "numeric",
                numerical_pipeline,
                numerical_features,
            ),
            (
                "categorical",
                categorical_pipeline,
                categorical_features,
            ),
        ]
    )


# ============================================================
# MODELS
# ============================================================

def create_models():
    """Create all classification models."""

    logistic = LogisticRegression(
        max_iter=5000,
        class_weight="balanced",
        random_state=RANDOM_STATE,
    )

    decision_tree = DecisionTreeClassifier(
        max_depth=6,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=RANDOM_STATE,
    )

    random_forest = RandomForestClassifier(
        n_estimators=400,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    voting = VotingClassifier(
        estimators=[
            (
                "logistic",
                LogisticRegression(
                    max_iter=5000,
                    class_weight="balanced",
                    random_state=RANDOM_STATE,
                ),
            ),
            (
                "decision_tree",
                DecisionTreeClassifier(
                    max_depth=6,
                    min_samples_leaf=2,
                    class_weight="balanced",
                    random_state=RANDOM_STATE,
                ),
            ),
            (
                "random_forest",
                RandomForestClassifier(
                    n_estimators=400,
                    min_samples_leaf=2,
                    class_weight="balanced",
                    random_state=RANDOM_STATE,
                    n_jobs=-1,
                ),
            ),
        ],
        voting="soft",
    )

    return {
        "Logistic Regression": logistic,
        "Decision Tree": decision_tree,
        "Random Forest": random_forest,
        "Voting Classifier": voting,
    }


# ============================================================
# PIPELINE
# ============================================================

def create_pipeline(
    X: pd.DataFrame,
    model,
    scale_numeric: bool = False,
) -> Pipeline:
    """
    Create preprocessing + model pipeline.

    Logistic Regression receives scaled numerical features.
    Tree-based models do not need scaling.
    """

    if scale_numeric:

        preprocessor = build_scaled_preprocessor(
            X
        )

    else:

        preprocessor = build_preprocessor(
            X
        )

    return Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor,
            ),
            (
                "model",
                model,
            ),
        ]
    )


# ============================================================
# EVALUATION
# ============================================================

def evaluate_model(
    name: str,
    model: Pipeline,
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
    cv: StratifiedKFold,
) -> dict:
    """Train and evaluate one classifier."""

    print()
    print("-" * 70)
    print(name)
    print("-" * 70)

    # --------------------------------------------------------
    # Train
    # --------------------------------------------------------

    model.fit(
        X_train,
        y_train,
    )

    # --------------------------------------------------------
    # Test prediction
    # --------------------------------------------------------

    predictions = model.predict(
        X_test
    )

    # --------------------------------------------------------
    # Test metrics
    # --------------------------------------------------------

    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    precision = precision_score(
        y_test,
        predictions,
        average="weighted",
        zero_division=0,
    )

    recall = recall_score(
        y_test,
        predictions,
        average="weighted",
        zero_division=0,
    )

    f1 = f1_score(
        y_test,
        predictions,
        average="weighted",
        zero_division=0,
    )

    # --------------------------------------------------------
    # Cross-validation
    # --------------------------------------------------------

    cv_scores = cross_val_score(
        model,
        X_train,
        y_train,
        cv=cv,
        scoring="accuracy",
        n_jobs=1,
    )

    # --------------------------------------------------------
    # Output
    # --------------------------------------------------------

    print(
        f"Test Accuracy : {accuracy:.4f}"
    )

    print(
        f"Test Precision: {precision:.4f}"
    )

    print(
        f"Test Recall   : {recall:.4f}"
    )

    print(
        f"Test F1-score : {f1:.4f}"
    )

    print(
        f"CV Accuracy   : "
        f"{cv_scores.mean():.4f} "
        f"+/- {cv_scores.std():.4f}"
    )

    print()
    print("Classification Report:")
    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0,
        )
    )

    return {
        "model": name,

        "test_accuracy": float(
            accuracy
        ),

        "test_precision": float(
            precision
        ),

        "test_recall": float(
            recall
        ),

        "test_f1": float(
            f1
        ),

        "cv_accuracy_mean": float(
            cv_scores.mean()
        ),

        "cv_accuracy_std": float(
            cv_scores.std()
        ),

        "cv_scores": [
            float(score)
            for score in cv_scores
        ],

        "confusion_matrix": (
            confusion_matrix(
                y_test,
                predictions,
            ).tolist()
        ),
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("REPOSITORY HEALTH CLASSIFICATION")
    print("=" * 70)

    # --------------------------------------------------------
    # Dataset
    # --------------------------------------------------------

    df = load_dataset()

    print(
        f"Repositories: {len(df)}"
    )

    print(
        f"Dataset columns: {len(df.columns)}"
    )

    # --------------------------------------------------------
    # Class distribution
    # --------------------------------------------------------

    print()
    print("Class distribution:")

    print(
        df[TARGET]
        .value_counts()
        .to_string()
    )

    # --------------------------------------------------------
    # Features
    # --------------------------------------------------------

    feature_columns = get_feature_columns(
        df
    )

    X = df[
        feature_columns
    ].copy()

    y = df[
        TARGET
    ].astype(str)

    numeric_features, categorical_features = (
        get_column_types(X)
    )

    print()
    print(
        f"Features used: {len(feature_columns)}"
    )

    print(
        f"Numeric features: {len(numeric_features)}"
    )

    print(
        f"Categorical features: "
        f"{len(categorical_features)}"
    )

    # --------------------------------------------------------
    # Validate class counts
    # --------------------------------------------------------

    class_counts = (
        y.value_counts()
    )

    if class_counts.min() < 2:

        raise ValueError(
            "At least one class has fewer than "
            "2 samples."
        )

    # --------------------------------------------------------
    # 80/20 stratified split
    # --------------------------------------------------------

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=TEST_SIZE,
            random_state=RANDOM_STATE,
            stratify=y,
        )
    )

    print()
    print("=" * 70)
    print("TRAIN / TEST SPLIT")
    print("=" * 70)

    print(
        f"Total samples : {len(X)}"
    )

    print(
        f"Training      : {len(X_train)}"
    )

    print(
        f"Testing       : {len(X_test)}"
    )

    print(
        f"Training %    : "
        f"{len(X_train) / len(X) * 100:.1f}%"
    )

    print(
        f"Testing %     : "
        f"{len(X_test) / len(X) * 100:.1f}%"
    )

    print()
    print("Training classes:")

    print(
        y_train.value_counts()
        .to_string()
    )

    print()
    print("Testing classes:")

    print(
        y_test.value_counts()
        .to_string()
    )

    # --------------------------------------------------------
    # Stratified CV
    # --------------------------------------------------------

    minimum_class_count = (
        y_train.value_counts().min()
    )

    cv_folds = min(
        4,
        int(minimum_class_count)
    )

    if cv_folds < 2:

        raise ValueError(
            "Not enough samples per class "
            "for stratified cross-validation."
        )

    cv = StratifiedKFold(
        n_splits=cv_folds,
        shuffle=True,
        random_state=RANDOM_STATE,
    )

    print()
    print(
        f"Cross-validation: "
        f"{cv_folds}-fold stratified"
    )

    # --------------------------------------------------------
    # Models
    # --------------------------------------------------------

    models = create_models()

    results = []

    fitted_models = {}

    # --------------------------------------------------------
    # Evaluation
    # --------------------------------------------------------

    for name, estimator in models.items():

        use_scaling = (
            name == "Logistic Regression"
        )

        pipeline = create_pipeline(
            X_train,
            estimator,
            scale_numeric=use_scaling,
        )

        result = evaluate_model(
            name,
            pipeline,
            X_train,
            X_test,
            y_train,
            y_test,
            cv,
        )

        results.append(
            result
        )

        fitted_models[name] = pipeline

    # --------------------------------------------------------
    # Comparison
    # --------------------------------------------------------

    results_df = pd.DataFrame(
        results
    ).sort_values(
        "test_accuracy",
        ascending=False,
    )

    print()
    print("=" * 70)
    print("MODEL COMPARISON")
    print("=" * 70)

    print(
        results_df[
            [
                "model",
                "test_accuracy",
                "test_precision",
                "test_recall",
                "test_f1",
                "cv_accuracy_mean",
                "cv_accuracy_std",
            ]
        ]
        .round(4)
        .to_string(index=False)
    )

    # --------------------------------------------------------
    # Select best model
    # --------------------------------------------------------

    best_name = (
        results_df.iloc[0]["model"]
    )

    print()
    print("=" * 70)
    print("BEST MODEL")
    print("=" * 70)

    print(
        f"Selected model: {best_name}"
    )

    best_result = next(
        result
        for result in results
        if result["model"] == best_name
    )

    print(
        f"Test Accuracy : "
        f"{best_result['test_accuracy']:.4f}"
    )

    print(
        f"Test F1-score : "
        f"{best_result['test_f1']:.4f}"
    )

    print(
        f"CV Accuracy   : "
        f"{best_result['cv_accuracy_mean']:.4f}"
    )

    # --------------------------------------------------------
    # Final training on all repositories
    # --------------------------------------------------------

    print()
    print(
        "Training final model on all repositories..."
    )

    final_scaling = (
        best_name == "Logistic Regression"
    )

    final_model = create_pipeline(
        X,
        models[best_name],
        scale_numeric=final_scaling,
    )

    final_model.fit(
        X,
        y,
    )

    print(
        "Final model trained."
    )

    # --------------------------------------------------------
    # Save model
    # --------------------------------------------------------

    MODEL_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        final_model,
        MODEL_FILE,
    )

    # --------------------------------------------------------
    # Save metrics
    # --------------------------------------------------------

    metrics = {
        "task": "classification",

        "target": TARGET,

        "samples": int(
            len(df)
        ),

        "training_samples": int(
            len(X_train)
        ),

        "testing_samples": int(
            len(X_test)
        ),

        "test_size": TEST_SIZE,

        "random_state": RANDOM_STATE,

        "cv_folds": cv_folds,

        "features": feature_columns,

        "classes": sorted(
            y.unique().tolist()
        ),

        "selected_model": best_name,

        "models": results,
    }

    with open(
        METRICS_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            metrics,
            file,
            indent=2,
        )

    # --------------------------------------------------------
    # Save feature metadata
    # --------------------------------------------------------

    feature_metadata = {
        "task": "classification",

        "target": TARGET,

        "features": feature_columns,

        "numeric_features": numeric_features,

        "categorical_features": (
            categorical_features
        ),

        "classes": sorted(
            y.unique().tolist()
        ),

        "selected_model": best_name,
    }

    with open(
        FEATURE_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            feature_metadata,
            file,
            indent=2,
        )

    # --------------------------------------------------------
    # Final output
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("FILES SAVED")
    print("=" * 70)

    print(
        f"Model   : {MODEL_FILE}"
    )

    print(
        f"Metrics : {METRICS_FILE}"
    )

    print(
        f"Features: {FEATURE_FILE}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()