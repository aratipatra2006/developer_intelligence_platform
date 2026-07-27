import os
import uuid
from git import Repo

CLONE_PATH = "repositories"


def clone_repository(repo_url):
    try:
        os.makedirs(CLONE_PATH, exist_ok=True)

        # Remove trailing slash
        repo_url = repo_url.rstrip("/")

        # Remove .git if present
        if repo_url.endswith(".git"):
            repo_url = repo_url[:-4]

        # Extract owner and repository
        parts = repo_url.split("/")
        owner = parts[-2]
        repo = parts[-1]

        # Unique folder name
        folder_name = f"{owner}_{repo}".lower()

        repo_path = os.path.join(CLONE_PATH, folder_name)

        if os.path.exists(repo_path):
            print("Repository already exists.")
            return True, repo_path

        Repo.clone_from(
            repo_url,
            repo_path,
            depth=1
        )
        return True, repo_path
    except Exception as e:
        return False, str(e)