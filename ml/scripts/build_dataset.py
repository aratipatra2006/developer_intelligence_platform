import csv
import gc
import os
import stat
import sys
import time
import traceback
import shutil


# PROJECT ROOT

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../..",
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# IMPORTS

from ml.scripts.github_api import get_github_data

from analyzer.clone_repo import clone_repository
from analyzer.repository_statistics import repository_statistics
from analyzer.readme_analyzer import analyze_readme
from analyzer.dependency_analyzer import analyze_dependencies
from analyzer.complexity_analyzer import analyze_complexity
from analyzer.language_detector import detect_languages
from analyzer.tech_stack import detect_tech_stack
from analyzer.repository_overview import get_repository_overview
from analyzer.health_score import (
    calculate_health_score,
    classify_health,
)


# PATHS

# Repository URL list collected by collect_repository_urls.py
REPOSITORY_LIST = os.path.join(
    PROJECT_ROOT,
    "ml",
    "dataset",
    "repositories.txt",
)

OUTPUT_FILE = os.path.join(
    PROJECT_ROOT,
    "ml",
    "data",
    "repository_dataset.csv",
)

FAILURE_FILE = os.path.join(
    PROJECT_ROOT,
    "ml",
    "data",
    "extraction_failures.csv",
)


# CSV COLUMNS

FIELDNAMES = [
    "repository",
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
    "has_readme",
    "has_license",
    "has_gitignore",
    "stars",
    "forks",
    "watchers",
    "open_issues",
    "language",
    "size",
    "created_days",
    "updated_days",
    "health_score",
    "health_grade",
    "complexity_supported",
    "functions_supported",
]


# HELPERS

def normalize_repository(value):
    """
    Convert a GitHub URL or repository name into
    a normalized owner/repo identifier.
    """

    value = str(value).strip()

    value = value.replace(
        "https://github.com/",
        "",
    )

    value = value.replace(
        "http://github.com/",
        "",
    )

    value = value.replace(
        "github.com/",
        "",
    )

    value = value.strip("/")

    if value.endswith(".git"):
        value = value[:-4]

    return value.lower()


def load_repositories():
    """
    Load unique repositories from repositories.txt.

    Deduplication is based on normalized owner/repo,
    so URL/case/.git variations are treated as the same
    repository.
    """

    if not os.path.exists(REPOSITORY_LIST):
        raise FileNotFoundError(
            f"Repository list not found:\n"
            f"{REPOSITORY_LIST}"
        )

    repositories = []
    seen = set()

    with open(
        REPOSITORY_LIST,
        "r",
        encoding="utf-8",
    ) as file:

        for line in file:
            repo = line.strip()

            if not repo:
                continue

            if repo.startswith("#"):
                continue

            normalized = normalize_repository(repo)

            if not normalized:
                continue

            if normalized in seen:
                continue

            seen.add(normalized)
            repositories.append(repo)

    return repositories


def load_completed_repositories():
    """
    Read successfully extracted repositories from
    repository_dataset.csv.

    This allows the script to resume without repeating
    completed repositories.
    """

    completed = set()

    if not os.path.exists(OUTPUT_FILE):
        return completed

    try:
        with open(
            OUTPUT_FILE,
            "r",
            newline="",
            encoding="utf-8",
        ) as file:

            reader = csv.DictReader(file)

            if not reader.fieldnames:
                return completed

            for row in reader:

                repository = row.get(
                    "repository",
                    "",
                )

                if repository:
                    completed.add(
                        normalize_repository(
                            repository
                        )
                    )

    except Exception as exc:
        print(
            "⚠️ Could not read existing dataset:",
            exc,
        )

    return completed


def prepare_output_files():
    """
    Create output files only if they don't exist.

    Existing dataset contents are never overwritten.
    """

    os.makedirs(
        os.path.dirname(OUTPUT_FILE),
        exist_ok=True,
    )

    os.makedirs(
        os.path.dirname(FAILURE_FILE),
        exist_ok=True,
    )

    # Dataset

    if not os.path.exists(OUTPUT_FILE):

        with open(
            OUTPUT_FILE,
            "w",
            newline="",
            encoding="utf-8",
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=FIELDNAMES,
            )

            writer.writeheader()

        print(
            "Created new dataset CSV."
        )

    else:
        print(
            "Existing dataset found — keeping it."
        )

    # Failure log

    if not os.path.exists(FAILURE_FILE):

        with open(
            FAILURE_FILE,
            "w",
            newline="",
            encoding="utf-8",
        ) as file:

            writer = csv.writer(file)

            writer.writerow(
                [
                    "repository",
                    "stage",
                    "error",
                ]
            )


def save_failure(repo, stage, error):
    """
    Append one failed repository to the failure log.
    """

    with open(
        FAILURE_FILE,
        "a",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.writer(file)

        writer.writerow(
            [
                repo,
                stage,
                str(error),
            ]
        )


def append_row(row):
    """
    Append exactly one successful repository row.

    Opening and closing the file for every row means
    progress remains saved if the process stops.
    """

    with open(
        OUTPUT_FILE,
        "a",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=FIELDNAMES,
        )

        writer.writerow(row)


# CLEANUP

def _remove_readonly(func, path, exc_info):
    """
    Remove a read-only file on Windows and retry.
    """

    try:
        os.chmod(
            path,
            stat.S_IWRITE,
        )
        func(path)

    except OSError:
        os.chmod(
            path,
            stat.S_IWRITE,
        )
        func(path)


def cleanup_repository(repo_path, retries=3):
    """
    Remove a temporary repository clone safely.

    Returns:
        True if successfully removed.
        False otherwise.
    """

    if not repo_path:
        return True

    if not os.path.exists(repo_path):
        return True

    # Give Python a chance to release temporary/file handles.
    gc.collect()

    for attempt in range(1, retries + 1):

        try:
            shutil.rmtree(
                repo_path,
                onerror=_remove_readonly,
            )

            return True

        except OSError as exc:

            if attempt == retries:
                print(
                    f"⚠️ Cleanup failed for "
                    f"{repo_path}: {exc}"
                )

                return False

            time.sleep(1)

    return False


# PROCESS ONE REPOSITORY

def process_repository(
    repo,
    index,
    total,
):
    """
    Extract all required features for one repository.

    The cloned repository is temporary working data and
    is removed after processing, including when an analyzer
    fails.
    """

    repo_path = None

    print()
    print("=" * 70)
    print(
        f"[{index}/{total}] Processing: {repo}"
    )
    print("=" * 70)

    try:


        # GitHub API


        try:
            data = get_github_data(repo)

            if data is None:
                raise RuntimeError(
                    "GitHub API returned no data."
                )

            print("✅ GitHub API")

        except Exception as exc:

            save_failure(
                repo,
                "github_api",
                exc,
            )

            print(
                f"❌ GitHub API failed: {exc}"
            )

            return False


        # Clone


        try:

            success, repo_result = (
                clone_repository(repo)
            )

            if not success:
                raise RuntimeError(
                    f"Clone failed for {repo}: "
                    f"{repo_result}"
                )

            repo_path = repo_result

            print("✅ Clone")

        except Exception as exc:

            save_failure(
                repo,
                "clone",
                exc,
            )

            print(
                f"❌ Clone failed: {exc}"
            )

            return False


        # Statistics


        try:

            stats = repository_statistics(
                repo_path
            )

            print("✅ Statistics")

        except Exception as exc:

            save_failure(
                repo,
                "statistics",
                exc,
            )

            print(
                f"❌ Statistics failed: {exc}"
            )

            return False


        # README


        try:

            readme = analyze_readme(
                repo_path
            )

            print(
                f"✅ README "
                f"({readme.get('score', 0)}/100)"
            )

        except Exception as exc:

            save_failure(
                repo,
                "readme",
                exc,
            )

            print(
                f"❌ README failed: {exc}"
            )

            return False


        # Dependencies


        try:

            dependencies = analyze_dependencies(
                repo_path
            )

            print(
                f"✅ Dependencies "
                f"({len(dependencies)})"
            )

        except Exception as exc:

            save_failure(
                repo,
                "dependencies",
                exc,
            )

            print(
                f"❌ Dependencies failed: {exc}"
            )

            return False


        # Complexity


        try:

            complexity = analyze_complexity(
                repo_path
            )

            print("✅ Complexity")

        except Exception as exc:

            save_failure(
                repo,
                "complexity",
                exc,
            )

            print(
                f"❌ Complexity failed: {exc}"
            )

            return False


        # Languages


        try:

            languages = detect_languages(
                repo_path
            )

            print(
                f"✅ Languages "
                f"({len(languages)})"
            )

        except Exception as exc:

            save_failure(
                repo,
                "language_detection",
                exc,
            )

            print(
                f"❌ Language detection failed: {exc}"
            )

            return False


        # Tech stack


        try:

            tech = detect_tech_stack(
                repo_path
            )

            print(
                f"✅ Tech Stack "
                f"({len(tech)})"
            )

        except Exception as exc:

            save_failure(
                repo,
                "tech_stack",
                exc,
            )

            print(
                f"❌ Tech stack failed: {exc}"
            )

            return False


        # Repository overview


        try:

            overview = get_repository_overview(
                repo_path
            )

            print(
                "✅ Repository Overview"
            )

        except Exception as exc:

            save_failure(
                repo,
                "repository_overview",
                exc,
            )

            print(
                f"❌ Repository overview failed: {exc}"
            )

            return False


        # Build dataset row


        try:

            complexity_value = complexity.get(
                "complexity",
                None,
            )

            functions_value = complexity.get(
                "functions",
                None,
            )

            complexity_supported = (
                complexity_value is not None
                and complexity_value != "Not Supported"
                and complexity_value != "-"
            )

            functions_supported = (
                functions_value is not None
                and functions_value != "Not Supported"
                and functions_value != "-"
            )

            # ----------------------------------------------------
            # Health score
            # ----------------------------------------------------

            health_features = {
                "readme_score": readme.get(
                    "score",
                    0,
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

                "complexity": complexity_value,

                "dependency_count": len(
                    dependencies
                ),

                "updated_days": data.get(
                    "updated_days",
                    0,
                ),
            }

            health_score = calculate_health_score(
                health_features
            )

            health_grade = classify_health(
                health_score
            )

            # ----------------------------------------------------
            # Dataset row
            # ----------------------------------------------------

            row = {
                "repository": data.get(
                    "repository",
                    repo,
                ),

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

                "functions": functions_value,

                "complexity": complexity_value,

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

                "stars": data.get(
                    "stars",
                    0,
                ),

                "forks": data.get(
                    "forks",
                    0,
                ),

                "watchers": data.get(
                    "watchers",
                    0,
                ),

                "open_issues": data.get(
                    "open_issues",
                    0,
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

                "health_score": health_score,

                "health_grade": health_grade,

                "complexity_supported": (
                    complexity_supported
                ),

                "functions_supported": (
                    functions_supported
                ),
            }

            append_row(row)

            print(
                "✅ Dataset row saved"
            )

            print(
                f"   Health: "
                f"{health_score:.2f} "
                f"({health_grade})"
            )

            return True

        except Exception as exc:

            save_failure(
                repo,
                "row_creation",
                exc,
            )

            print(
                f"❌ Dataset row failed: {exc}"
            )

            traceback.print_exc()

            return False

    finally:

        # ========================================================
        # CLEANUP
        # ========================================================

        if repo_path:

            if cleanup_repository(
                repo_path
            ):

                print(
                    f"🧹 Cleaned clone: "
                    f"{repo_path}"
                )


# MAIN

def main():

    start_time = time.time()

    print()
    print("=" * 70)
    print(
        "RESUMABLE REPOSITORY DATASET BUILDER"
    )
    print("=" * 70)

    print(
        f"Input : {REPOSITORY_LIST}"
    )

    print(
        f"Output: {OUTPUT_FILE}"
    )

    print()

    # Load repositories

    repositories = load_repositories()

    print(
        f"Repositories in list: "
        f"{len(repositories)}"
    )

    # Prepare output files

    prepare_output_files()

    # Find completed repositories

    completed = (
        load_completed_repositories()
    )

    print(
        f"Already completed: "
        f"{len(completed)}"
    )

    # Determine remaining repositories

    remaining = [
        repo
        for repo in repositories
        if normalize_repository(repo)
        not in completed
    ]

    print(
        f"Remaining: "
        f"{len(remaining)}"
    )

    # Nothing left

    if not remaining:

        print()
        print(
            "✅ All repositories are already extracted."
        )

        return

    # Process remaining repositories

    successful = 0
    failed = 0

    total_remaining = len(
        remaining
    )

    for index, repo in enumerate(
        remaining,
        start=1,
    ):

        success = process_repository(
            repo,
            index,
            total_remaining,
        )

        if success:
            successful += 1

        else:
            failed += 1

    # Summary

    elapsed = (
        time.time()
        - start_time
    )

    print()
    print("=" * 70)
    print(
        "EXTRACTION COMPLETE"
    )
    print("=" * 70)

    print(
        f"Processed : "
        f"{total_remaining}"
    )

    print(
        f"Successful: "
        f"{successful}"
    )

    print(
        f"Failed    : "
        f"{failed}"
    )

    print(
        f"Time      : "
        f"{elapsed / 60:.2f} minutes"
    )

    print()

    print(
        f"Dataset   : "
        f"{OUTPUT_FILE}"
    )

    print(
        f"Failures  : "
        f"{FAILURE_FILE}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()