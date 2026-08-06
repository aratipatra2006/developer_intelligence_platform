import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()

TOKEN = os.getenv("GITHUB_TOKEN")

if not TOKEN:
    raise Exception("GITHUB_TOKEN not found in .env file")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json"
}

# File Paths
INPUT_FILE = "ml/dataset/repositories.txt"
OUTPUT_FILE = "ml/dataset/repositories_metadata.csv"

os.makedirs("ml/dataset", exist_ok=True)

# Read Repository URLs
if not os.path.exists(INPUT_FILE):
    raise FileNotFoundError(f"{INPUT_FILE} not found.")

with open(INPUT_FILE, "r", encoding="utf-8") as file:
    repositories = [line.strip() for line in file if line.strip()]

print("=" * 60)
print(f"Total repositories found : {len(repositories)}")
print("=" * 60)

# Resume Support
processed = set()
data = []

if os.path.exists(OUTPUT_FILE):

    old_df = pd.read_csv(OUTPUT_FILE)

    if "url" in old_df.columns:
        processed = set(old_df["url"].astype(str))

    data = old_df.to_dict("records")

    print(f"Already processed : {len(processed)}")

# Statistics
success = 0
skipped = 0
failed = 0

# Collect Metadata
for index, repo_url in enumerate(repositories, start=1):

    if repo_url in processed:
        continue

    try:

        owner, repo = repo_url.rstrip("/").split("/")[-2:]

        api_url = f"https://api.github.com/repos/{owner}/{repo}"

        response = requests.get(
            api_url,
            headers=HEADERS,
            timeout=30
        )

        # Rate Limit Handling
        if response.status_code == 403:

            remaining = response.headers.get(
                "X-RateLimit-Remaining",
                "?"
            )

            reset = response.headers.get(
                "X-RateLimit-Reset"
            )

            print("\nGitHub Rate Limit Reached!")
            print("Remaining:", remaining)

            if reset:
                wait = max(
                    int(reset) - int(time.time()) + 5,
                    5
                )

                print(f"Sleeping for {wait} seconds...\n")

                time.sleep(wait)

                response = requests.get(
                    api_url,
                    headers=HEADERS,
                    timeout=30
                )

        if response.status_code != 200:

            print(
                f"[{index}] Skipped ({response.status_code}) : {repo_url}"
            )

            skipped += 1
            continue

        repo_data = response.json()

        data.append({

            "repository": repo_data.get("full_name"),
            "url": repo_data.get("html_url"),
            "language": repo_data.get("language"),
            "stars": repo_data.get("stargazers_count"),
            "forks": repo_data.get("forks_count"),
            "watchers": repo_data.get("watchers_count"),
            "open_issues": repo_data.get("open_issues_count"),
            "size": repo_data.get("size"),
            "created_at": repo_data.get("created_at"),
            "updated_at": repo_data.get("updated_at"),
            "license": repo_data["license"]["name"] if repo_data.get("license") else None,
            "default_branch": repo_data.get("default_branch"),
            "archived": repo_data.get("archived"),
            "fork": repo_data.get("fork")
        })

        success += 1

        print(
            f"[{index}/{len(repositories)}] "
            f"✓ {repo_data.get('full_name')}"
        )

        # Save every 100 repositories
        if len(data) % 100 == 0:

            pd.DataFrame(data).to_csv(
                OUTPUT_FILE,
                index=False
            )

            print(f"\nSaved {len(data)} repositories...\n")

        time.sleep(0.4)

    except Exception as e:

        failed += 1

        print(
            f"[{index}] Failed : {repo_url}"
        )

        print(e)

# Final Save
pd.DataFrame(data).to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n" + "=" * 60)
print("Metadata collection completed!")
print("=" * 60)
print(f"Repositories processed : {len(data)}")
print(f"Success               : {success}")
print(f"Skipped               : {skipped}")
print(f"Failed                : {failed}")
print(f"Output                : {OUTPUT_FILE}")
print("=" * 60)