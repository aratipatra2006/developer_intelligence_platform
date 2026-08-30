"""
Explainable baseline health scoring for repositories.

This module creates a deterministic 0-100 repository health score from
features extracted by the repository analyzer pipeline.

The score is intended to provide a reproducible baseline label for ML
experiments. It is not objective ground truth for software quality.
"""

from __future__ import annotations

from typing import Any, Mapping


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _to_bool(value: Any) -> bool:
    """Convert common representations into a boolean."""
    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        return value != 0

    if isinstance(value, str):
        return value.strip().lower() in {
            "true",
            "1",
            "yes",
            "y",
        }

    return False


def _to_float(
    value: Any,
    default: float = 0.0,
) -> float:
    """Safely convert a value to float."""
    try:
        if value is None or value == "":
            return default

        return float(value)

    except (TypeError, ValueError):
        return default


def _clamp(
    value: float,
    minimum: float,
    maximum: float,
) -> float:
    """Clamp a numeric value to a range."""
    return max(minimum, min(maximum, value))


# ---------------------------------------------------------------------------
# Documentation — 25 points
# ---------------------------------------------------------------------------

def _documentation_score(
    features: Mapping[str, Any],
) -> float:
    """
    Documentation quality: 25 points.

    README quality : 15
    License        : 5
    Contributing / supporting documentation : 5

    Note:
    has_readme is intentionally NOT scored here separately because
    readme_score already incorporates README existence.
    """

    readme_score = _clamp(
        _to_float(
            features.get("readme_score")
        ),
        0.0,
        100.0,
    )

    score = (
        readme_score / 100.0
    ) * 15.0

    # License availability
    if _to_bool(features.get("has_license")):
        score += 5.0

    # Use a small bonus for meaningful project documentation signals.
    # This remains optional because the current dataset does not expose
    # separate contributing/usage fields.
    documentation_bonus = 0.0

    if _to_bool(features.get("has_gitignore")):
        documentation_bonus += 5.0

    score += documentation_bonus

    return round(
        _clamp(score, 0.0, 25.0),
        2,
    )


# ---------------------------------------------------------------------------
# Code quality — 35 points
# ---------------------------------------------------------------------------

def _complexity_score(
    features: Mapping[str, Any],
) -> float:
    """
    Code quality: 35 points.

    25 points from average complexity.
    10 points from rough code organization signals.

    Unsupported complexity receives a neutral complexity score rather
    than being treated as excellent or terrible.
    """

    raw = features.get("complexity")

    try:
        complexity = float(raw)

    except (TypeError, ValueError):
        complexity_score = 12.5
    else:
        if complexity <= 3:
            complexity_score = 25.0
        elif complexity <= 5:
            complexity_score = 22.0
        elif complexity <= 8:
            complexity_score = 18.0
        elif complexity <= 12:
            complexity_score = 13.0
        elif complexity <= 20:
            complexity_score = 7.0
        else:
            complexity_score = 2.0

    # -------------------------------------------------------
    # Organization signal — 10 points
    # -------------------------------------------------------

    total_files = max(
        0.0,
        _to_float(
            features.get("total_files")
        ),
    )

    total_folders = max(
        0.0,
        _to_float(
            features.get("total_folders")
        ),
    )

    lines = max(
        0.0,
        _to_float(
            features.get("lines")
        ),
    )

    functions = max(
        0.0,
        _to_float(
            features.get("functions")
        ),
    )

    organization_score = 0.0

    # Files/folders relationship.
    if total_files > 0:
        folder_ratio = (
            total_folders / total_files
        )

        if 0.03 <= folder_ratio <= 0.5:
            organization_score += 5.0
        elif folder_ratio <= 0.8:
            organization_score += 3.0
        else:
            organization_score += 1.0

    # Functions relative to code volume.
    if lines > 0 and functions > 0:
        functions_per_10k_lines = (
            functions / lines
        ) * 10000

        if functions_per_10k_lines >= 2:
            organization_score += 5.0
        elif functions_per_10k_lines >= 0.5:
            organization_score += 3.0
        else:
            organization_score += 1.0

    return round(
        _clamp(
            complexity_score + organization_score,
            0.0,
            35.0,
        ),
        2,
    )


# ---------------------------------------------------------------------------
# Dependency health — 20 points
# ---------------------------------------------------------------------------

def _dependency_score(
    features: Mapping[str, Any],
) -> float:
    """
    Dependency hygiene: 20 points.

    This is intentionally a coarse signal.

    Fewer dependencies are not automatically better, but extremely large
    dependency sets can increase maintenance complexity.

    A value of zero is treated conservatively because zero can mean either
    genuinely no detected dependencies or incomplete detection.
    """

    raw = features.get("dependency_count")

    try:
        count = float(raw)

    except (TypeError, ValueError):
        return 10.0

    count = max(0.0, count)

    if count == 0:
        return 12.0

    if count <= 10:
        return 20.0

    if count <= 20:
        return 17.0

    if count <= 40:
        return 14.0

    if count <= 80:
        return 10.0

    if count <= 150:
        return 6.0

    return 3.0


# ---------------------------------------------------------------------------
# Project hygiene — 15 points
# ---------------------------------------------------------------------------

def _project_hygiene_score(
    features: Mapping[str, Any],
) -> float:
    """
    Project hygiene: 15 points.

    License     : 5
    .gitignore  : 5
    README      : 5

    README existence is treated as hygiene here, while README quality
    itself is handled separately by documentation_score.
    """

    score = 0.0

    if _to_bool(features.get("has_readme")):
        score += 5.0

    if _to_bool(features.get("has_license")):
        score += 5.0

    if _to_bool(features.get("has_gitignore")):
        score += 5.0

    return score


# ---------------------------------------------------------------------------
# Activity — 5 points
# ---------------------------------------------------------------------------

def _activity_score(
    features: Mapping[str, Any],
) -> float:
    """
    Recent repository activity: 5 points.

    Activity is intentionally given a small weight because recent commits
    do not necessarily imply good software quality.
    """

    updated_days = _to_float(
        features.get("updated_days"),
        default=-1.0,
    )

    if updated_days < 0:
        return 2.5

    if updated_days <= 7:
        return 5.0

    if updated_days <= 30:
        return 4.5

    if updated_days <= 90:
        return 4.0

    if updated_days <= 180:
        return 3.5

    if updated_days <= 365:
        return 2.5

    if updated_days <= 730:
        return 1.5

    return 0.5


# ---------------------------------------------------------------------------
# Final score
# ---------------------------------------------------------------------------

def calculate_health_score(
    features: Mapping[str, Any],
) -> float:
    """
    Calculate a reproducible 0-100 repository health score.

    Weighting:
        Documentation      25
        Code quality       35
        Dependencies       20
        Project hygiene    15
        Activity             5
        ----------------------
        Total              100
    """

    score = (
        _documentation_score(features)
        + _complexity_score(features)
        + _dependency_score(features)
        + _project_hygiene_score(features)
        + _activity_score(features)
    )

    return round(
        _clamp(score, 0.0, 100.0),
        2,
    )


def classify_health(
    score: float,
) -> str:
    """Map a numeric health score to a human-readable band."""

    value = _to_float(score)

    if value >= 85:
        return "Excellent"

    if value >= 70:
        return "Good"

    if value >= 55:
        return "Moderate"

    if value >= 40:
        return "Needs Improvement"

    return "Poor"