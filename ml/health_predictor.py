"""
Repository health prediction.

Loads the trained Random Forest classification pipeline and predicts
the repository health grade from repository features extracted by the
analyzer pipeline.

The trained model predicts one of:

    Excellent
    Good
    Moderate
    Needs Improvement
    Poor
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

import joblib
import pandas as pd


# ============================================================================
# Paths
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

MODEL_FILE = (
    PROJECT_ROOT
    / "ml"
    / "health_model.pkl"
)

FEATURE_FILE = (
    PROJECT_ROOT
    / "ml"
    / "health_model_features.json"
)


# ============================================================================
# Model loading
# ============================================================================

def load_model():
    """Load the trained health classification pipeline."""

    if not MODEL_FILE.exists():
        raise FileNotFoundError(
            f"Trained model not found:\n{MODEL_FILE}\n\n"
            "Run ml/train_health_model.py first."
        )

    return joblib.load(MODEL_FILE)


# ============================================================================
# Feature metadata
# ============================================================================

def load_feature_metadata() -> dict[str, Any]:
    """
    Load the feature metadata saved during training.

    This ensures prediction uses the same feature set as training.
    """

    if not FEATURE_FILE.exists():
        raise FileNotFoundError(
            f"Feature metadata not found:\n{FEATURE_FILE}\n\n"
            "Run ml/train_health_model.py first."
        )

    with open(
        FEATURE_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


# ============================================================================
# Prepare input
# ============================================================================

def prepare_features(
    features: Mapping[str, Any],
) -> pd.DataFrame:
    """
    Convert a repository feature dictionary into the exact
    one-row DataFrame expected by the trained classification pipeline.
    """

    metadata = load_feature_metadata()

    numeric_features = metadata.get(
        "numeric_features",
        [],
    )

    categorical_features = metadata.get(
        "categorical_features",
        [],
    )

    expected_features = (
        list(numeric_features)
        + list(categorical_features)
    )

    if not expected_features:
        raise ValueError(
            "No trained feature metadata found."
        )

    # --------------------------------------------------------
    # Create exactly one input row.
    # --------------------------------------------------------

    row = {}

    for column in expected_features:

        row[column] = features.get(
            column,
            None,
        )

    df = pd.DataFrame(
        [row],
        columns=expected_features,
    )

    # --------------------------------------------------------
    # Convert numeric columns.
    # --------------------------------------------------------

    for column in numeric_features:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            )

    # --------------------------------------------------------
    # Keep categorical columns suitable for OneHotEncoder.
    # --------------------------------------------------------

    for column in categorical_features:

        if column in df.columns:

            df[column] = df[column].astype(
                "object"
            )

    return df


# ============================================================================
# Classification prediction
# ============================================================================

def predict_health(
    features: Mapping[str, Any],
) -> str:
    """
    Predict repository health grade.

    Returns one of:

        Excellent
        Good
        Moderate
        Needs Improvement
        Poor
    """

    model = load_model()

    X = prepare_features(
        features
    )

    prediction = model.predict(
        X
    )[0]

    # Convert NumPy/string-like values to a normal Python string.
    grade = str(
        prediction
    ).strip()

    valid_grades = {
        "Excellent",
        "Good",
        "Moderate",
        "Needs Improvement",
        "Poor",
    }

    if grade not in valid_grades:

        raise ValueError(
            f"Unexpected health grade returned by model: "
            f"{grade!r}"
        )

    return grade


# ============================================================================
# Complete result
# ============================================================================

def predict_health_details(
    features: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Return complete classification prediction information.

    The classifier predicts the health grade directly.
    No numeric score is produced by the ML model.
    """

    grade = predict_health(
        features
    )

    return {
        "grade": grade,
    }