import os
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

API_BASE = "https://api.github.com"


def get_headers():
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    return headers


def get_github_data(repo_url):
    """
    Fetch repository information from GitHub REST API.
    """

    repo = (
        repo_url
        .replace("https://github.com/", "")
        .replace("http://github.com/", "")
        .strip("/")
    )

    if repo.endswith(".git"):
        repo = repo[:-4]

    api = f"{API_BASE}/repos/{repo}"

    try:
        response = requests.get(
            api,
            headers=get_headers(),
            timeout=20,
        )
    except requests.RequestException as exc:
        print(f"GitHub API connection error: {exc}")
        return None

    if response.status_code != 200:
        print(
            f"GitHub API Error: {response.status_code} "
            f"for {repo}"
        )

        try:
            error_data = response.json()
            print(
                "Message:",
                error_data.get("message", "Unknown error")
            )
        except ValueError:
            pass

        # Show rate-limit information
        remaining = response.headers.get(
            "X-RateLimit-Remaining"
        )
        reset = response.headers.get(
            "X-RateLimit-Reset"
        )

        print(
            f"Rate limit remaining: {remaining}"
        )

        if reset:
            print(
                f"Rate limit reset timestamp: {reset}"
            )

        return None

    try:
        data = response.json()

        created = datetime.strptime(
            data["created_at"],
            "%Y-%m-%dT%H:%M:%SZ"
        ).replace(tzinfo=timezone.utc)

        updated = datetime.strptime(
            data["updated_at"],
            "%Y-%m-%dT%H:%M:%SZ"
        ).replace(tzinfo=timezone.utc)

        today = datetime.now(timezone.utc)

        age_days = round(
            (today - created).total_seconds() / 86400,
            2
        )
        updated_days = round(
            (today - updated).total_seconds() / 86400,
            2
        )

        return {
            "repository": data["full_name"],
            "stars": data["stargazers_count"],
            "forks": data["forks_count"],
            "watchers": data["watchers_count"],
            "open_issues": data["open_issues_count"],
            "language": data["language"],
            "size": data["size"],
            "created_days": age_days,
            "updated_days": updated_days,
        }

    except (KeyError, ValueError, TypeError) as exc:
        print(
            f"GitHub API data parsing error for {repo}: {exc}"
        )
        return None