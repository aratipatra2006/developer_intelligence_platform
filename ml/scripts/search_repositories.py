import requests
import time

# -------------------------
# Your GitHub Personal Access Token
# -------------------------
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("GITHUB_TOKEN")
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json"
}

languages = [
    "Python",
    "Java",
    "JavaScript",
    "C++",
    "Go"
]

all_repositories = []

for language in languages:

    print(f"\nCollecting {language} repositories...")

    for page in range(1, 6):

        url = "https://api.github.com/search/repositories"

        params = {
            "q": f"language:{language} stars:>100 archived:false",
            "sort": "stars",
            "order": "desc",
            "per_page": 20,
            "page": page
        }

        response = requests.get(
            url,
            headers=headers,
            params=params
        )

        if response.status_code != 200:

            print(response.text)
            break

        data = response.json()

        items = data.get("items", [])

        if len(items) == 0:
            break

        for repo in items:

            all_repositories.append(repo["html_url"])

        print(f"Page {page} : {len(items)} repositories")

        time.sleep(1)

print("\nTotal repositories collected:", len(all_repositories))

with open("../dataset/repositories.txt", "w") as file:

    for repo in sorted(set(all_repositories)):
        file.write(repo + "\n")

print("repositories.txt created successfully.")