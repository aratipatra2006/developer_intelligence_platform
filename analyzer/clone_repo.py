import os
import uuid
from git import Repo

CLONE_PATH = "repositories"


def clone_repository(repo_url):
    try:
        os.makedirs(CLONE_PATH, exist_ok=True)
        repo_name = repo_url.rstrip("/").split("/")[-1]

        repo_path = os.path.join(
        CLONE_PATH,
        repo_name
         )
        if not os.path.exists(repo_path):

         Repo.clone_from(
        repo_url,
        repo_path,
        depth=1
    )
        return True, repo_path

    except Exception as e:
        return False, str(e)