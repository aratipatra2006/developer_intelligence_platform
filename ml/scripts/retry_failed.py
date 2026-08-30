import csv
import os
import sys
import time

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ml.scripts.github_api import get_github_data

from analyzer.clone_repo import clone_repository
from analyzer.repository_statistics import repository_statistics
from analyzer.readme_analyzer import analyze_readme
from analyzer.dependency_analyzer import analyze_dependencies
from analyzer.complexity_analyzer import analyze_complexity
from analyzer.language_detector import detect_languages
from analyzer.tech_stack import detect_tech_stack
from analyzer.repository_overview import get_repository_overview


DATASET_FILE = os.path.join(
    PROJECT_ROOT,
    "ml",
    "data",
    "repository_dataset.csv"
)

FAILURE_FILE = os.path.join(
    PROJECT_ROOT,
    "ml",
    "data",
    "extraction_failures.csv"
)

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
]


def load_failures():
    repos = []

    if not os.path.exists(FAILURE_FILE):
        print("No extraction_failures.csv found.")
        return repos

    with open(
        FAILURE_FILE,
        "r",
        encoding="utf-8",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:
            repo = row.get("repository", "").strip()

            if repo:
                repos.append(repo)

    return list(dict.fromkeys(repos))


def append_row(row):
    with open(
        DATASET_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=FIELDNAMES
        )

        writer.writerow(row)


def process(repo, index, total):

    print()
    print("=" * 65)
    print(f"[{index}/{total}] {repo}")
    print("=" * 65)

    # GitHub API
    try:
        data = get_github_data(repo)

        if data is None:
            print("❌ GitHub API failed")
            return False

        print("✅ GitHub API")

    except Exception as exc:
        print(f"❌ GitHub API exception: {exc}")
        return False

    # Clone
    try:
        success, repo_path = clone_repository(repo)

        if not success:
            print("❌ Clone failed")
            return False

        print("✅ Clone")

    except Exception as exc:
        print(f"❌ Clone exception: {exc}")
        return False

    # Statistics
    try:
        stats = repository_statistics(repo_path)
        print("✅ Statistics")

    except Exception as exc:
        print(f"❌ Statistics failed: {exc}")
        return False

    # README
    try:
        readme = analyze_readme(repo_path)
        print("✅ README")

    except Exception as exc:
        print(f"❌ README failed: {exc}")
        return False

    # Dependencies
    try:
        dependencies = analyze_dependencies(repo_path)
        print(f"✅ Dependencies: {len(dependencies)}")

    except Exception as exc:
        print(f"❌ Dependencies failed: {exc}")
        return False

    # Complexity
    try:
        complexity = analyze_complexity(repo_path)
        print("✅ Complexity")

    except Exception as exc:
        print(f"❌ Complexity failed: {exc}")
        return False

    # Languages
    try:
        languages = detect_languages(repo_path)
        print(f"✅ Languages: {len(languages)}")

    except Exception as exc:
        print(f"❌ Language detection failed: {exc}")
        return False

    # Tech stack
    try:
        tech = detect_tech_stack(repo_path)
        print(f"✅ Tech stack: {len(tech)}")

    except Exception as exc:
        print(f"❌ Tech stack failed: {exc}")
        return False

    # Overview
    try:
        overview = get_repository_overview(repo_path)
        print("✅ Overview")

    except Exception as exc:
        print(f"❌ Overview failed: {exc}")
        return False

    # Dataset row
    row = {
        "repository": data.get("repository", repo),

        "total_files": stats.get("total_files", 0),
        "total_folders": stats.get("total_folders", 0),
        "lines": stats.get("lines", 0),

        "python": stats.get("python", 0),
        "html": stats.get("html", 0),
        "css": stats.get("css", 0),
        "javascript": stats.get("javascript", 0),
        "java": stats.get("java", 0),
        "cpp": stats.get("cpp", 0),

        "dependency_count": len(dependencies),
        "readme_score": readme.get("score", 0),

        "functions": complexity.get("functions", 0),
        "complexity": complexity.get("complexity", 0),

        "language_count": len(languages),
        "tech_stack_count": len(tech),

        "has_readme": overview.get("README", False),
        "has_license": overview.get("License", False),
        "has_gitignore": overview.get(".gitignore", False),

        "stars": data.get("stars", 0),
        "forks": data.get("forks", 0),
        "watchers": data.get("watchers", 0),
        "open_issues": data.get("open_issues", 0),

        "language": data.get("language", ""),
        "size": data.get("size", 0),

        "created_days": data.get("created_days", 0),
        "updated_days": data.get("updated_days", 0),
    }

    append_row(row)

    print("✅ Dataset row saved")

    return True


def main():

    failures = load_failures()

    print()
    print("=" * 65)
    print("RETRY FAILED REPOSITORIES")
    print("=" * 65)
    print(f"Repositories to retry: {len(failures)}")
    print()

    if not failures:
        return

    success = 0
    failed = 0

    for index, repo in enumerate(
        failures,
        start=1
    ):

        if process(
            repo,
            index,
            len(failures)
        ):
            success += 1
        else:
            failed += 1

        # Small delay between repositories
        time.sleep(1)

    print()
    print("=" * 65)
    print("RETRY COMPLETE")
    print("=" * 65)
    print(f"Successful: {success}")
    print(f"Failed:     {failed}")
    print("=" * 65)


if __name__ == "__main__":
    main()