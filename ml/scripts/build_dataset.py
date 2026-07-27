import csv
import os
import sys
import csv
import os
import sys

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from github_api import get_github_data

from analyzer.clone_repo import clone_repository
from analyzer.repository_statistics import repository_statistics
from analyzer.readme_analyzer import analyze_readme
from analyzer.dependency_analyzer import analyze_dependencies
from analyzer.complexity_analyzer import analyze_complexity
from analyzer.language_detector import detect_languages
from analyzer.tech_stack import detect_tech_stack
from analyzer.repository_overview import get_repository_overview

repositories = []

with open("../../dataset/repositories.txt", "r") as file:

    for line in file:
        repositories.append(line.strip())

with open("../data/repository_dataset.csv",
          "w",
          newline="",
          encoding="utf-8") as csvfile:

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

    for repo in repositories:

        print("\n===================================")
        print("Processing:", repo)

        data = get_github_data(repo)
        print("✅ GitHub API Done")

        if data is None:
            continue

        success, repo_path = clone_repository(repo)
        print("✅ Clone Done")

        if not success:
            print("Clone failed:", repo)
            continue

        stats = repository_statistics(repo_path)
        print("✅ Statistics Done")

        readme = analyze_readme(repo_path)
        print("✅ README Done")

        dependencies = analyze_dependencies(repo_path)
        print("✅ Dependencies Done")

        complexity = analyze_complexity(repo_path)
        print("✅ Complexity Done")

        languages = detect_languages(repo_path)
        print("✅ Language Detection Done")

        tech = detect_tech_stack(repo_path)
        print("✅ Tech Stack Done")

        overview = get_repository_overview(repo_path)
        print("✅ Repository Overview Done")
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

print("Dataset Created Successfully!")