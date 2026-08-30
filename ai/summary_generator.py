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

    # ===========================
    # Project Overview
    # ===========================

    project_name = overview["Repository Name"].replace("-", " ")

    languages_used = (
        ", ".join(languages.keys())
        if languages
        else "multiple languages"
    )

    tech_used = (
        ", ".join(tech[:4])
        if tech
        else "modern technologies"
    )

    overview_text = (
        f"'{project_name}' is a software project developed primarily using "
        f"{languages_used}. It leverages {tech_used} and currently contains "
        f"{statistics['total_files']} files organized into "
        f"{statistics['total_folders']} folders."
    )

    # Documentation insight
    if overview["README"]:
        overview_text += " The project includes a README for documentation."
    else:
        overview_text += (
            " Documentation is limited because a README file is missing."
        )

    # Maintainability insight
    avg_complexity = complexity["complexity"]

    if avg_complexity < 5:
        overview_text += " The codebase appears clean and easy to maintain."
    elif avg_complexity < 10:
        overview_text += " The codebase has moderate complexity."
    else:
        overview_text += (
            " Some modules have high complexity and may benefit from refactoring."
        )

    summary["project_overview"] = overview_text

    # ===========================
    # Documentation
    # ===========================

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

    # ===========================
    # Programming Languages
    # ===========================

    if languages:
        lang_text = ", ".join(languages.keys())
        summary["languages"] = (
            f"The project is mainly developed using {lang_text}."
        )
    else:
        summary["languages"] = "No programming languages detected."

    # ===========================
    # Technology Stack
    # ===========================

    if tech:
        summary["technology"] = (
            "Detected technologies include "
            + ", ".join(tech)
            + "."
        )
    else:
        summary["technology"] = "No technologies detected."

    # ===========================
    # Dependencies
    # ===========================

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

    # ===========================
    # Code Quality
    # ===========================

    if avg_complexity < 5:
        quality_status = (
            "The code has low complexity and is easy to maintain."
        )
    elif avg_complexity < 10:
        quality_status = (
            "The code has moderate complexity. Some functions may require optimization."
        )
    else:
        quality_status = (
            "The code has high complexity. Refactoring is recommended."
        )

    summary["quality"] = (
        f"The repository contains {complexity['functions']} functions "
        f"with an average complexity of {avg_complexity}. "
        f"{quality_status}"
    )

    # ===========================
    # Repository Health Score
    # ===========================

    score = 100

    if not overview["README"]:
        score -= 15

    if not overview["License"]:
        score -= 10

    if not overview[".gitignore"]:
        score -= 5

    if avg_complexity > 10:
        score -= 20

    summary["health_score"] = score

    # ===========================
    # Suggestions
    # ===========================

       # ===========================
    # AI Suggestions
    # ===========================

    suggestions = []

    # Documentation
    if not overview["README"]:
        suggestions.append(
            " Add a README file to improve project documentation."
        )

    if not overview["License"]:
        suggestions.append(
            " Include a LICENSE file to clarify usage and distribution rights."
        )

    if not overview[".gitignore"]:
        suggestions.append(
            "Add a .gitignore file to avoid committing unnecessary files."
        )

    # Code Quality
    if avg_complexity > 10:
        suggestions.append(
            "Refactor complex functions to improve readability and maintainability."
        )
    elif avg_complexity > 5:
        suggestions.append(
            " Consider simplifying moderately complex functions where possible."
        )

    # Dependencies
    if len(dependencies) == 0:
        suggestions.append(
            " No external dependencies detected. Verify if all required libraries are included."
        )

    # Languages
    if len(languages) == 1:
        suggestions.append(
            " Consider separating frontend and backend technologies if the project grows."
        )

    # Technology Recommendations
    if "Spring Boot" in tech:
        suggestions.append(
            "Add JUnit tests to improve code reliability."
        )

        suggestions.append(
            "Add Swagger/OpenAPI documentation for REST APIs."
        )

        suggestions.append(
            "Configure GitHub Actions for automatic build and testing."
        )

    if "React" in tech:
        suggestions.append(
            "Optimize React components using lazy loading and code splitting."
        )

    if "Flask" in tech:
        suggestions.append(
            " Use environment variables for secret keys and database credentials."
        )

    # Security
    suggestions.append(
        " Ensure sensitive credentials are stored securely using environment variables."
    )

    # General Best Practices
    suggestions.append(
        " Add logging to improve debugging and production monitoring."
    )

    suggestions.append(
        " Consider Docker support for easier deployment."
    )

    suggestions.append(
        " Add CI/CD pipelines for automated testing and deployment."
    )

    # Positive Feedback
    if len(suggestions) <= 3:
        suggestions.append(
            " Repository follows good development practices overall."
        )

    summary["suggestions"] = suggestions

    return summary