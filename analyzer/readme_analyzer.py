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

    for file in os.listdir(repo_path):

        if file.lower().startswith("readme"):
            readme_path = os.path.join(repo_path, file)
            break

    if not readme_path:
        return result

    result["exists"] = True

    with open(readme_path, "r", encoding="utf-8", errors="ignore") as f:

        text = f.read()

    result["word_count"] = len(text.split())

    lower = text.lower()

    if "installation" in lower:
        result["installation"] = True

    if "usage" in lower:
        result["usage"] = True

    if "license" in lower:
        result["license"] = True

    if "contributing" in lower:
        result["contributing"] = True

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