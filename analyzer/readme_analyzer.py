"""
README analyzer.

Finds README files recursively, prioritizing the repository root and then
the nearest nested README. Produces a deterministic 0-100 documentation
score used by the repository analysis and ML pipeline.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any


# Directories that should never be searched for documentation.
IGNORED_DIRS = {
    ".git",
    ".github",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    "dist",
    "build",
    "target",
    "vendor",
    "coverage",
}


README_NAMES = {
    "readme",
    "readme.md",
    "readme.txt",
    "readme.rst",
    "readme.markdown",
}


def _find_readme(repo_path: str) -> Path | None:
    """
    Find the most appropriate README.

    Priority:
        1. README in repository root
        2. README in the nearest nested directory
        3. Among equally deep candidates, prefer README.md
    """

    root = Path(repo_path)

    # ---------------------------------------------------------------
    # First check repository root.
    # ---------------------------------------------------------------

    root_candidates = []

    try:
        for item in root.iterdir():

            if not item.is_file():
                continue

            if item.name.lower() in README_NAMES:
                root_candidates.append(item)

    except OSError:
        return None

    if root_candidates:
        # Prefer README.md at root.
        root_candidates.sort(
            key=lambda p: (
                p.name.lower() != "readme.md",
                p.name.lower(),
            )
        )

        return root_candidates[0]

    # ---------------------------------------------------------------
    # Search nested directories.
    # ---------------------------------------------------------------

    candidates: list[Path] = []

    for current_root, dirs, files in os.walk(root):

        # Modify dirs in-place so os.walk does not enter ignored dirs.
        dirs[:] = [
            directory
            for directory in dirs
            if directory not in IGNORED_DIRS
        ]

        current_path = Path(current_root)

        for filename in files:

            if filename.lower() not in README_NAMES:
                continue

            candidates.append(
                current_path / filename
            )

    if not candidates:
        return None

    # Prefer the shallowest README.
    # At equal depth prefer README.md.
    candidates.sort(
        key=lambda path: (
            len(path.relative_to(root).parts),
            path.name.lower() != "readme.md",
            str(path).lower(),
        )
    )

    return candidates[0]


def _contains_any(
    text: str,
    phrases: list[str],
) -> bool:
    """Return True if any phrase occurs in the text."""

    return any(
        phrase in text
        for phrase in phrases
    )


def analyze_readme(
    repo_path: str,
) -> dict[str, Any]:
    """
    Analyze repository README content.

    Score breakdown:

        README exists                         10
        300+ words                            20
        100+ words                            10
        installation/setup instructions      15
        usage/examples                        15
        features/overview                     10
        license information                   10
        contributing/development information 10

    Total: 100
    """

    result: dict[str, Any] = {
        "exists": False,
        "path": None,
        "word_count": 0,
        "installation": False,
        "usage": False,
        "features": False,
        "license": False,
        "contributing": False,
        "score": 0,
    }

    readme_path = _find_readme(
        repo_path
    )

    if readme_path is None:
        return result

    result["exists"] = True

    # Store relative path for debugging/UI.
    try:
        result["path"] = str(
            readme_path.relative_to(
                Path(repo_path)
            )
        )
    except ValueError:
        result["path"] = str(readme_path)

    # ---------------------------------------------------------------
    # Read file
    # ---------------------------------------------------------------

    try:

        text = readme_path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

    except OSError:
        return result

    lower = text.lower()

    result["word_count"] = len(
        text.split()
    )

    # ---------------------------------------------------------------
    # Installation / setup
    # ---------------------------------------------------------------

    result["installation"] = _contains_any(
        lower,
        [
            "installation",
            "install",
            "setup",
            "getting started",
            "quick start",
            "prerequisites",
            "requirements",
        ],
    )

    # ---------------------------------------------------------------
    # Usage / examples
    # ---------------------------------------------------------------

    result["usage"] = _contains_any(
        lower,
        [
            "usage",
            "how to use",
            "example",
            "examples",
            "quickstart",
            "quick start",
            "run the",
            "running the",
        ],
    )

    # ---------------------------------------------------------------
    # Features / project overview
    # ---------------------------------------------------------------

    result["features"] = _contains_any(
        lower,
        [
            "features",
            "what it does",
            "overview",
            "about",
            "highlights",
            "functionality",
        ],
    )

    # ---------------------------------------------------------------
    # License
    # ---------------------------------------------------------------

    result["license"] = _contains_any(
        lower,
        [
            "license",
            "licence",
            "mit license",
            "apache license",
            "gpl",
            "bsd license",
        ],
    )

    # ---------------------------------------------------------------
    # Contributing / development
    # ---------------------------------------------------------------

    result["contributing"] = _contains_any(
        lower,
        [
            "contributing",
            "contribution",
            "development",
            "developing",
            "pull request",
            "issue tracker",
        ],
    )

    # ---------------------------------------------------------------
    # Score
    # ---------------------------------------------------------------

    score = 0

    # README exists.
    score += 10

    # Length / substance.
    if result["word_count"] >= 300:
        score += 20
    elif result["word_count"] >= 100:
        score += 10

    # Installation / setup.
    if result["installation"]:
        score += 15

    # Usage / examples.
    if result["usage"]:
        score += 15

    # Features / overview.
    if result["features"]:
        score += 10

    # License information.
    if result["license"]:
        score += 10

    # Contributing/development.
    if result["contributing"]:
        score += 10

    result["score"] = min(
        score,
        100,
    )

    return result