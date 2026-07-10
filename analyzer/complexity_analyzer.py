import os
from radon.complexity import cc_visit


def analyze_complexity(repo_path):

    total_complexity = 0
    total_functions = 0

    for root, dirs, files in os.walk(repo_path):

        if ".git" in dirs:
            dirs.remove(".git")

        for file in files:

            if file.endswith(".py"):

                filepath = os.path.join(root, file)

                try:

                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:

                        source = f.read()

                    results = cc_visit(source)

                    for item in results:

                        total_complexity += item.complexity
                        total_functions += 1

                except Exception:
                    pass

    average = 0

    if total_functions > 0:

        average = round(total_complexity / total_functions, 2)

    return {
        "functions": total_functions,
        "complexity": average
    }