import requests
import csv

# Read repository URLs from the text file
with open("dataset/repositories.txt", "r") as file:
    repositories = [line.strip() for line in file if line.strip()]

# Create output CSV
with open("dataset/github_data.csv", "w", newline="", encoding="utf-8") as csvfile:

    writer = csv.writer(csvfile)

    writer.writerow([
        "repository",
        "stars",
        "forks",
        "watchers",
        "open_issues",
        "language",
        "size"
    ])

    for repo_url in repositories:

        repo = repo_url.replace("https://github.com/", "").replace(".git", "")

        api = f"https://api.github.com/repos/{repo}"

        print(f"Fetching {repo}...")

        response = requests.get(api)

        if response.status_code != 200:
            print("Failed:", repo)
            continue

        data = response.json()

        writer.writerow([
            data["full_name"],
            data["stargazers_count"],
            data["forks_count"],
            data["watchers_count"],
            data["open_issues_count"],
            data["language"],
            data["size"]
        ])

        print("Saved:", data["full_name"])

print("\nDataset created successfully!")