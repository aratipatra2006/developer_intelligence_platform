import requests
from datetime import datetime

def get_github_data(repo_url):
    """
    Fetch repository information from GitHub REST API.
    """

    repo = repo_url.replace("https://github.com/", "").replace(".git", "")

    api = f"https://api.github.com/repos/{repo}"

    response = requests.get(api)

    if response.status_code != 200:
        print("GitHub API Error:", response.status_code)
        return None

    data = response.json()

    # Repository age
    created = datetime.strptime(
        data["created_at"],
        "%Y-%m-%dT%H:%M:%SZ"
    )

    updated = datetime.strptime(
        data["updated_at"],
        "%Y-%m-%dT%H:%M:%SZ"
    )

    today = datetime.utcnow()

    age_days = (today - created).days
    updated_days = (today - updated).days

    return {

        "repository": data["full_name"],

        "stars": data["stargazers_count"],

        "forks": data["forks_count"],

        "watchers": data["watchers_count"],

        "open_issues": data["open_issues_count"],

        "language": data["language"],

        "size": data["size"],

        "created_days": age_days,

        "updated_days": updated_days

    }