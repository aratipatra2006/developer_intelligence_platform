import os

def get_repository_overview(repo_path):
    """
    Returns basic repository information.
    """

    repo_name = os.path.basename(repo_path)

    readme_exists = False
    license_exists = False
    gitignore_exists = False

    for root, dirs, files in os.walk(repo_path):

        for file in files:

            filename = file.lower()

            if filename.startswith("readme"):
                readme_exists = True

            if filename == "license":
                license_exists = True

            if filename == ".gitignore":
                gitignore_exists = True

    return {

        "Repository Name": repo_name,
        "README": readme_exists,
        "License": license_exists,
        ".gitignore": gitignore_exists

    }