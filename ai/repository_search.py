import os
import re

# Folders we don't want to search
IGNORE_DIRS = {
    ".git",
    "node_modules",
    "venv",
    "__pycache__",
    "dist",
    "build",
    ".idea",
    ".vscode"
}

# Files that are useful for repository questions
ALLOWED_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".cpp",
    ".c",
    ".h",
    ".html",
    ".css",
    ".json",
    ".md",
    ".yml",
    ".yaml"
}


def get_repository_files(repo_path):
    """Get searchable source files from the repository."""

    files = []

    for root, dirs, filenames in os.walk(repo_path):

        # Ignore unnecessary directories
        dirs[:] = [
            directory
            for directory in dirs
            if directory not in IGNORE_DIRS
        ]

        for filename in filenames:

            extension = os.path.splitext(filename)[1].lower()

            if extension in ALLOWED_EXTENSIONS:
                files.append(
                    os.path.join(root, filename)
                )

    return files


def search_repository(repo_path, query, max_results=8):
    """
    Search repository files using simple keyword matching.
    Returns the most relevant files.
    """

    if not repo_path or not os.path.exists(repo_path):
        return []

    query_words = re.findall(
        r"\b\w+\b",
        query.lower()
    )

    results = []

    for file_path in get_repository_files(repo_path):

        try:
            with open(
                file_path,
                "r",
                encoding="utf-8",
                errors="ignore"
            ) as file:

                content = file.read()

        except Exception:
            continue

        lower_content = content.lower()

        score = 0

        # Score matching words
        for word in query_words:

            if len(word) < 3:
                continue

            score += lower_content.count(word)

        # Give extra importance to filename matches
        filename = os.path.basename(file_path).lower()

        for word in query_words:

            if len(word) >= 3 and word in filename:
                score += 10

        if score > 0:

            results.append(
                (
                    score,
                    file_path,
                    content
                )
            )

    # Highest score first
    results.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return results[:max_results]