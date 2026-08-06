import os


def analyze_readme(repo_path):

    result = {
        "exists": False,
        "word_count": 0,
        "installation": False,
        "usage": False,
        "license": False,
        "contributing": False,
        "score": 0
    }

    readme_path = None

    # Search for README files only
    for file in os.listdir(repo_path):

        full_path = os.path.join(repo_path, file)

        if (
            file.lower().startswith("readme")
            and os.path.isfile(full_path)
        ):
            readme_path = full_path
            break

    if readme_path is None:
        return result

    result["exists"] = True

    try:

        with open(
            readme_path,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as f:

            text = f.read()

    except Exception:
        return result

    result["word_count"] = len(text.split())

    lower = text.lower()

    result["installation"] = "installation" in lower
    result["usage"] = "usage" in lower
    result["license"] = "license" in lower
    result["contributing"] = "contributing" in lower

    score = 0

    if result["exists"]:
        score += 20

    if result["word_count"] > 300:
        score += 20

    if result["installation"]:
        score += 20

    if result["usage"]:
        score += 20

    if result["license"]:
        score += 10

    if result["contributing"]:
        score += 10

    result["score"] = score

    return result