import os


def repository_statistics(repo_path):

    stats = {
        "total_files": 0,
        "total_folders": 0,
        "python": 0,
        "html": 0,
        "css": 0,
        "javascript": 0,
        "java": 0,
        "cpp": 0,
        "lines": 0
    }

    skip_dirs = {
        ".git",
        "__pycache__",
        "venv",
        ".venv",
        "node_modules",
        "dist",
        "build"
    }

    for root, dirs, files in os.walk(repo_path):

        dirs[:] = [d for d in dirs if d not in skip_dirs]

        stats["total_folders"] += len(dirs)

        for file in files:

            stats["total_files"] += 1

            path = os.path.join(root, file)

            if file.endswith(".py"):
                stats["python"] += 1

            elif file.endswith(".html"):
                stats["html"] += 1

            elif file.endswith(".css"):
                stats["css"] += 1

            elif file.endswith(".js"):
                stats["javascript"] += 1

            elif file.endswith(".java"):
                stats["java"] += 1

            elif file.endswith(".cpp"):
                stats["cpp"] += 1

            try:

                with open(
                    path,
                    "r",
                    encoding="utf-8",
                    errors="ignore"
                ) as f:

                    stats["lines"] += len(f.readlines())

            except:
                pass

    return stats