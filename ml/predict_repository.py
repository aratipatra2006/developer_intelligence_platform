"""
Analyze a GitHub repository and predict its health using the trained model.

This is the command-line bridge between the existing repository analyzers
and the trained Random Forest model.

Usage:
    python ml/predict_repository.py https://github.com/pallets/flask
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


# ============================================================================
# Project paths
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================================
# Existing analyzers
# ============================================================================

from analyzer.clone_repo import clone_repository
from analyzer.repository_statistics import repository_statistics
from analyzer.readme_analyzer import analyze_readme
from analyzer.dependency_analyzer import analyze_dependencies
from analyzer.complexity_analyzer import analyze_complexity
from analyzer.language_detector import detect_languages
from analyzer.tech_stack import detect_tech_stack
from analyzer.repository_overview import get_repository_overview

from ml.health_predictor import (
    predict_health_details,
)


# ============================================================================
# Helpers
# ============================================================================

def print_section(title: str) -> None:
    """Print a formatted section heading."""

    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def build_features(
    repo_path: str,
    github_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Run the existing repository analyzers and build the model feature
    dictionary.
    """

    print_section("EXTRACTING REPOSITORY FEATURES")

    # ------------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------------

    stats = repository_statistics(repo_path)

    print("✅ Repository statistics")

    # ------------------------------------------------------------------------
    # README
    # ------------------------------------------------------------------------

    readme = analyze_readme(repo_path)

    print("✅ README analysis")

    # ------------------------------------------------------------------------
    # Dependencies
    # ------------------------------------------------------------------------

    dependencies = analyze_dependencies(repo_path)

    print(
        f"✅ Dependencies: {len(dependencies)}"
    )

    # ------------------------------------------------------------------------
    # Complexity
    # ------------------------------------------------------------------------

    complexity = analyze_complexity(repo_path)

    print("✅ Complexity analysis")

    # ------------------------------------------------------------------------
    # Languages
    # ------------------------------------------------------------------------

    languages = detect_languages(repo_path)

    print(
        f"✅ Languages: {len(languages)}"
    )

    # ------------------------------------------------------------------------
    # Tech stack
    # ------------------------------------------------------------------------

    tech = detect_tech_stack(repo_path)

    print(
        f"✅ Tech stack: {len(tech)}"
    )

    # ------------------------------------------------------------------------
    # Overview
    # ------------------------------------------------------------------------

    overview = get_repository_overview(repo_path)

    print("✅ Repository overview")

    # ------------------------------------------------------------------------
    # Build feature dictionary
    # ------------------------------------------------------------------------

    data = github_data or {}

    features = {
        "total_files": stats.get(
            "total_files",
            0,
        ),

        "total_folders": stats.get(
            "total_folders",
            0,
        ),

        "lines": stats.get(
            "lines",
            0,
        ),

        "python": stats.get(
            "python",
            0,
        ),

        "html": stats.get(
            "html",
            0,
        ),

        "css": stats.get(
            "css",
            0,
        ),

        "javascript": stats.get(
            "javascript",
            0,
        ),

        "java": stats.get(
            "java",
            0,
        ),

        "cpp": stats.get(
            "cpp",
            0,
        ),

        "dependency_count": len(
            dependencies
        ),

        "readme_score": readme.get(
            "score",
            0,
        ),

        "functions": complexity.get(
            "functions",
            None,
        ),

        "complexity": complexity.get(
            "complexity",
            None,
        ),

        "language_count": len(
            languages
        ),

        "tech_stack_count": len(
            tech
        ),

        "has_readme": overview.get(
            "README",
            False,
        ),

        "has_license": overview.get(
            "License",
            False,
        ),

        "has_gitignore": overview.get(
            ".gitignore",
            False,
        ),

        "language": data.get(
            "language",
            "",
        ),

        "size": data.get(
            "size",
            0,
        ),

        "created_days": data.get(
            "created_days",
            0,
        ),

        "updated_days": data.get(
            "updated_days",
            0,
        ),

        # These flags were added when the training dataset was cleaned.
        "complexity_supported": (
            complexity.get(
                "complexity",
                None,
            ) is not None
        ),

        "functions_supported": (
            complexity.get(
                "functions",
                None,
            ) is not None
        ),
    }

    return features


def get_github_data(repo_url: str) -> dict[str, Any] | None:
    """
    Fetch GitHub metadata for the repository.

    Uses the same authenticated GitHub API module used by the dataset
    generation pipeline.
    """

    from ml.scripts.github_api import (
        get_github_data as fetch_github_data,
    )

    return fetch_github_data(
        repo_url
    )


# ============================================================================
# Main
# ============================================================================

def main() -> None:

    if len(sys.argv) != 2:
        print(
            "Usage:"
        )
        print(
            "  python ml/predict_repository.py "
            "<github_url>"
        )
        sys.exit(1)

    repo_url = sys.argv[1].strip()

    print_section(
        "DEVELOPER INTELLIGENCE PLATFORM"
    )

    print(
        f"Repository: {repo_url}"
    )

    # ------------------------------------------------------------------------
    # GitHub metadata
    # ------------------------------------------------------------------------

    print_section(
        "GITHUB API"
    )

    github_data = get_github_data(
        repo_url
    )

    if github_data is None:
        print(
            "❌ Could not retrieve repository metadata."
        )
        sys.exit(1)

    print(
        "✅ GitHub metadata retrieved"
    )

    print(
        f"Language: {github_data.get('language')}"
    )

    print(
        f"Stars: {github_data.get('stars')}"
    )

    # ------------------------------------------------------------------------
    # Clone
    # ------------------------------------------------------------------------

    print_section(
        "REPOSITORY CLONE"
    )

    success, repo_path = clone_repository(
        repo_url
    )

    if not success:
        print(
            "❌ Repository cloning failed."
        )
        sys.exit(1)

    print(
        f"✅ Repository cloned"
    )

    print(
        f"Path: {repo_path}"
    )

    # ------------------------------------------------------------------------
    # Feature extraction
    # ------------------------------------------------------------------------

    features = build_features(
        repo_path,
        github_data,
    )

    # ------------------------------------------------------------------------
    # Prediction
    # ------------------------------------------------------------------------

    print_section(
        "HEALTH PREDICTION"
    )

    result = predict_health_details(
        features
    )

    print(
        f"Health Score : {result['score']:.2f}/100"
    )

    print(
        f"Health Grade : {result['grade']}"
    )

    # ------------------------------------------------------------------------
    # Feature summary
    # ------------------------------------------------------------------------

    print_section(
        "EXTRACTED FEATURES"
    )

    display_features = [
        "total_files",
        "total_folders",
        "lines",
        "dependency_count",
        "readme_score",
        "functions",
        "complexity",
        "language_count",
        "tech_stack_count",
        "has_readme",
        "has_license",
        "has_gitignore",
        "created_days",
        "updated_days",
    ]

    for name in display_features:
        print(
            f"{name:24}: {features.get(name)}"
        )

    print()
    print(
        "✅ End-to-end repository prediction completed."
    )


if __name__ == "__main__":
    main()