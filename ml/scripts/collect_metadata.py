import requests
import pandas as pd
import time
import os

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

data = []

with open("dataset/repositories.txt", "r") as file:
    repositories = [line.strip() for line in file.readlines()]

print(f"Total repositories: {len(repositories)}")

for index, repo_url in enumerate(repositories, start=1):

    owner, repo = repo_url.split("/")[-2:]

    api_url = f"https://api.github.com/repos/{owner}/{repo}"

    response = requests.get(api_url, headers=headers)

    if response.status_code != 200:
        print(f"Skipped: {repo_url}")
        continue

    repo = response.json()

    data.append({
        "repository": repo["full_name"],
        "url": repo["html_url"],
        "language": repo["language"],
        "stars": repo["stargazers_count"],
        "forks": repo["forks_count"],
        "watchers": repo["watchers_count"],
        "open_issues": repo["open_issues_count"],
        "size": repo["size"],
        "created_at": repo["created_at"],
        "updated_at": repo["updated_at"],
        "license": repo["license"]["name"] if repo["license"] else "None",
        "default_branch": repo["default_branch"],
        "archived": repo["archived"],
        "fork": repo["fork"]
    })

    print(f"{index}/{len(repositories)} : {repo['full_name']}")

    time.sleep(0.5)

df = pd.DataFrame(data)

df.to_csv("dataset/repositories_metadata.csv", index=False)

print("\nMetadata collection completed!")
print(f"Repositories saved: {len(df)}")