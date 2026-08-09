import os
import time
import requests
from dotenv import load_dotenv

# Load GitHub Token
load_dotenv()

TOKEN = os.getenv("GITHUB_TOKEN")

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json"
}

# Languages
languages = [
    "Python",
    "Java",
    "JavaScript",
    "TypeScript",
    "C++",
    "C",
    "Go",
    "Rust",
    "PHP",
    "Ruby",
    "Swift",
    "Kotlin",
    "Dart",
    "Scala",
    "C#"
]

# Star Ranges
star_ranges = [
    "10..50",
    "51..100",
    "101..500",
    "501..1000",
    "1001..5000",
    ">5000"
]

repositories = set()

# Search Repositories
for language in languages:

    print(f"\n========== {language} ==========")

    for stars in star_ranges:

        print(f"Stars: {stars}")

        for page in range(1, 6):

            url = "https://api.github.com/search/repositories"

            params = {
                "q": f"language:{language} stars:{stars} archived:false",
                "sort": "stars",
                "order": "desc",
                "per_page": 100,
                "page": page
            }

            response = requests.get(
                url,
                headers=headers,
                params=params
            )

            if response.status_code != 200:
                print("GitHub API Error:", response.text)
                break

            items = response.json().get("items", [])

            if not items:
                break

            for repo in items:
                repositories.add(repo["html_url"])

            print(
                f"Page {page} -> "
                f"{len(items)} repositories | "
                f"Total Unique: {len(repositories)}"
            )

            time.sleep(1)

# Save Dataset
output_dir = "ml/dataset"
os.makedirs(output_dir, exist_ok=True)

output_file = os.path.join(
    output_dir,
    "repositories.txt"
)

with open(output_file, "w") as file:
    for repo in sorted(repositories):
        file.write(repo + "\n")

print("\n======================================")
print("Unique repositories collected:", len(repositories))
print("Saved to:", output_file)
print("======================================")