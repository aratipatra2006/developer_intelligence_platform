import os
import requests
from datetime import datetime
from dotenv import load_dotenv
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load GitHub Token
load_dotenv()

TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json"
}


def get_github_data(repo_url):
    """
    Fetch repository information from GitHub REST API.
    """

    repo = repo_url.replace("https://github.com/", "").replace(".git", "")

    api = f"https://api.github.com/repos/{repo}"

    try:

        response = requests.get(
            api,
            headers=HEADERS,
            timeout=30,
            verify=False
        )

        if response.status_code != 200:
            print(f"GitHub API Error: {response.status_code}")
            return None

        data = response.json()

        created = datetime.strptime(
            data["created_at"],
            "%Y-%m-%dT%H:%M:%SZ"
        )

        updated = datetime.strptime(
            data["updated_at"],
            "%Y-%m-%dT%H:%M:%SZ"
        )

        today = datetime.utcnow()

        return {

            "repository": data["full_name"],
            "stars": data["stargazers_count"],
            "forks": data["forks_count"],
            "watchers": data["watchers_count"],
            "open_issues": data["open_issues_count"],
            "language": data["language"],
            "size": data["size"],
            "created_days": (today - created).days,
            "updated_days": (today - updated).days

        }

    except Exception as e:

        print("GitHub API Exception:", e)
        return None