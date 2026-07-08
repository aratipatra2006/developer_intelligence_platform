import os
import shutil
import uuid
from git import Repo

CLONE_PATH = "repositories"


def clone_repository(repo_url):
    try:

        repo_name = repo_url.rstrip("/").split("/")[-1]

        unique_id = str(uuid.uuid4())[:8]
        repo_path = os.path.join(
             CLONE_PATH,
             f"{repo_name}_{unique_id}"
         ) 

        Repo.clone_from(
    repo_url,
    repo_path,
    depth=1
)

        return True, repo_path

    except Exception as e:
        return False, str(e)