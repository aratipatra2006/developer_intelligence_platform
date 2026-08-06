import os
import csv
import sys
import traceback
import pandas as pd

# Add project root to Python path
sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "../.."
        )
    )
)

# Import project modules
from github_api import get_github_data

from analyzer.clone_repo import clone_repository
from analyzer.repository_statistics import repository_statistics
from analyzer.readme_analyzer import analyze_readme
from analyzer.dependency_analyzer import analyze_dependencies
from analyzer.complexity_analyzer import analyze_complexity
from analyzer.language_detector import detect_languages
from analyzer.tech_stack import detect_tech_stack
from analyzer.repository_overview import get_repository_overview

# File Paths
INPUT_FILE = "ml/dataset/repositories.txt"
OUTPUT_FILE = "ml/data/repository_dataset.csv"

os.makedirs("ml/data", exist_ok=True)

# Read repository list
with open(INPUT_FILE, "r", encoding="utf-8") as file:
    repositories = [
        line.strip()
        for line in file
        if line.strip()
    ]
print(f"Total repositories to process: {len(repositories)}")

# Resume Support
processed = set()

if os.path.exists(OUTPUT_FILE):

    df = pd.read_csv(OUTPUT_FILE)

    if "repository" in df.columns:
        processed = set(df["repository"])

    print(f"Already processed: {len(processed)}")

# Create CSV if it doesn't exist
if not os.path.exists(OUTPUT_FILE):

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as csvfile:

        writer = csv.writer(csvfile)

        writer.writerow([
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
            "updated_days"
        ])
# Statistics
success = 0
failed = 0

# Process repositories
for index, repo in enumerate(repositories, start=1):

    try:

        owner_repo = "/".join(repo.rstrip("/").split("/")[-2:])

        # Resume support
        if owner_repo in processed:
            continue

        print("\n" + "=" * 60)
        print(f"[{index}/{len(repositories)}]")
        print(f"Processing: {owner_repo}")

        # GitHub Metadata
        data = None

        for attempt in range(5):

            data = get_github_data(repo)

            if data is not None:
                break

            print(f"GitHub API failed. Retry {attempt + 1}/5...")
            time.sleep(5)

        if data is None:

            print("Skipping repository after 5 failed attempts.")

            with open("ml/data/failed_repositories.txt", "a") as f:
                f.write(repo + "\n")

            failed += 1
            continue

        print("✓ GitHub API")

        # Clone Repository
        success_clone, repo_path = clone_repository(repo)

        if not success_clone:
            print("Clone failed.")
            failed += 1
            continue

        print("✓ Repository")

        # Repository Statistics
        stats = repository_statistics(repo_path)
        print("✓ Statistics")

        # README
        readme = analyze_readme(repo_path)
        print("✓ README")

        # Dependencies
        dependencies = analyze_dependencies(repo_path)
        print("✓ Dependencies")

        # Complexity
        complexity = analyze_complexity(repo_path)
        print("✓ Complexity")

        # Languages
        languages = detect_languages(repo_path)
        print("✓ Languages")

        tech = detect_tech_stack(repo_path)
        print("✓ Tech Stack")

       
        overview = get_repository_overview(repo_path)
        print("✓ Overview")
        
        with open(
            OUTPUT_FILE,
            "a",
            newline="",
            encoding="utf-8"
        ) as csvfile:

            writer = csv.writer(csvfile)

            writer.writerow([
                data["repository"],
                stats["total_files"],
                stats["total_folders"],
                stats["lines"],
                stats["python"],
                stats["html"],
                stats["css"],
                stats["javascript"],
                stats["java"],
                stats["cpp"],
                len(dependencies),
                readme["score"],
                complexity["functions"],
                complexity["complexity"],
                len(languages),
                len(tech),
                overview["README"],
                overview["License"],
                overview[".gitignore"],
                data["stars"],
                data["forks"],
                data["watchers"],
                data["open_issues"],
                data["language"],
                data["size"],
                data["created_days"],
                data["updated_days"]
            ])

        success += 1
        processed.add(owner_repo)

        print("✓ Saved")

    except Exception as e:

        failed += 1

        print("\nRepository Failed:", repo)
        print(e)

        # Print complete error for debugging
        traceback.print_exc()

        continue

print("\n" + "=" * 60)
print("Dataset Creation Completed")
print("=" * 60)
print(f"Successful repositories : {success}")
print(f"Failed repositories     : {failed}")
print(f"Dataset saved to        : {OUTPUT_FILE}")
print("=" * 60)