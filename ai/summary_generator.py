def generate_ai_summary(
    overview,
    languages,
    tech,
    statistics,
    readme,
    complexity,
    dependencies
):

    summary = {}

    # Project Overview

    summary["project_overview"] = (
        f"This repository is named '{overview['Repository Name']}'. "
        f"It contains {statistics['total_files']} files and "
        f"{statistics['total_folders']} folders."
    )

    # Documentation

    doc = []

    if overview["README"]:
        doc.append("README file is available.")
    else:
        doc.append("README file is missing.")

    if overview["License"]:
        doc.append("License file is available.")
    else:
        doc.append("License file is missing.")

    if overview[".gitignore"]:
        doc.append(".gitignore file is available.")
    else:
        doc.append(".gitignore file is missing.")

    summary["documentation"] = " ".join(doc)

    # Languages

    if languages:
        lang_text = ", ".join(languages.keys())
        summary["languages"] = (
            f"The project is mainly developed using {lang_text}."
        )
    else:
        summary["languages"] = "No programming languages detected."

    # Technology Stack

    if tech:
        summary["technology"] = (
            "Detected technologies include "
            + ", ".join(tech)
            + "."
        )
    else:
        summary["technology"] = "No technologies detected."

    # Dependencies
  
    if dependencies:
        summary["dependencies"] = (
            "External libraries used are "
            + ", ".join(dependencies)
            + "."
        )
    else:
        summary["dependencies"] = (
            "No external dependencies were detected."
        )

        # Code Quality Analysis

    avg_complexity = complexity["complexity"]

    if avg_complexity < 5:
        quality_status = "The code has low complexity and is easy to maintain."
    
    elif avg_complexity < 10:
        quality_status = "The code has moderate complexity. Some functions may require optimization."
    
    else:
        quality_status = "The code has high complexity. Refactoring is recommended."

    summary["quality"] = (
        f"The repository contains {complexity['functions']} functions "
        f"with an average complexity of {avg_complexity}. "
        f"{quality_status}"
    )

    # Repository Health Score

    summary["quality"] = (
        f"The repository contains {complexity['functions']} functions "
        f"with an average complexity of "
        f"{complexity['complexity']}."
    )

    # Repository Health Score

    score = 100

    if not overview["README"]:
        score -= 15

    if not overview["License"]:
        score -= 10

    if not overview[".gitignore"]:
        score -= 5

    if complexity["complexity"] > 10:
        score -= 20

    summary["health_score"] = score

    # Suggestions

    suggestions = []

    if not overview["README"]:
        suggestions.append("Add a README file.")

    if not overview["License"]:
        suggestions.append("Add a LICENSE file.")

    if not overview[".gitignore"]:
        suggestions.append("Add a .gitignore file.")

    if len(suggestions) == 0:
        suggestions.append(
            "Repository structure looks good."
        )

    summary["suggestions"] = suggestions

    return summary