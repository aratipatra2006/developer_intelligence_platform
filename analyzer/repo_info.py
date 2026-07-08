import os


def repository_information(repo_path):

    total_files = 0

    total_folders = 0

    size = 0

    for root, dirs, files in os.walk(repo_path):

        total_folders += len(dirs)

        total_files += len(files)

        for file in files:

            file_path = os.path.join(root, file)

            size += os.path.getsize(file_path)

    return {

        "files": total_files,

        "folders": total_folders,

        "size": round(size / 1024, 2)

    }