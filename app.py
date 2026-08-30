from flask import Flask, render_template, request, redirect, url_for

import time

from analyzer.clone_repo import clone_repository
from analyzer.repo_info import repository_information
from analyzer.language_detector import detect_languages
from analyzer.tech_stack import detect_tech_stack
from analyzer.repository_overview import get_repository_overview
from analyzer.repository_statistics import repository_statistics
from analyzer.readme_analyzer import analyze_readme
from analyzer.dependency_analyzer import analyze_dependencies
from analyzer.complexity_analyzer import analyze_complexity
from analyzer.health_score import (
    calculate_health_score,
    classify_health,
)

from utils.validators import validate_github_url

from ai.summary_generator import generate_ai_summary

# ML
from ml.scripts.github_api import get_github_data
from ml.health_predictor import predict_health_details


# Flask application

app = Flask(__name__)

app.secret_key = "developer_intelligence"


# Most recently completed analysis
#
# Fine for the current single-user/local prototype.

LAST_CONTEXT = None


# Context helper

def get_context_or_redirect():
    """Return the most recently completed analysis context."""

    return LAST_CONTEXT


# ML feature vector

def build_ml_features(
    github_data,
    statistics,
    overview,
    readme,
    dependencies,
    complexity,
    languages,
    tech,
):
    """
    Build the exact feature dictionary expected by the trained
    classification model.
    """

    complexity_value = complexity.get(
        "complexity",
        None,
    )

    functions_value = complexity.get(
        "functions",
        None,
    )

    return {

        
        # Repository statistics
        

        "total_files": statistics.get(
            "total_files",
            0,
        ),

        "total_folders": statistics.get(
            "total_folders",
            0,
        ),

        "lines": statistics.get(
            "lines",
            0,
        ),

        
        # Language-specific counts
        

        "python": statistics.get(
            "python",
            0,
        ),

        "html": statistics.get(
            "html",
            0,
        ),

        "css": statistics.get(
            "css",
            0,
        ),

        "javascript": statistics.get(
            "javascript",
            0,
        ),

        "java": statistics.get(
            "java",
            0,
        ),

        "cpp": statistics.get(
            "cpp",
            0,
        ),

        
        # Dependencies
        

        "dependency_count": len(
            dependencies
        ),

        
        # README
        

        "readme_score": readme.get(
            "score",
            0,
        ),

        
        # Complexity
        

        "functions": functions_value,

        "complexity": complexity_value,

        
        # Counts
        

        "language_count": len(
            languages
        ),

        "tech_stack_count": len(
            tech
        ),

        
        # Repository hygiene
        

        "has_readme": overview.get(
            "README",
            False,
        ),

        "has_license": overview.get(
            "License",
            False,
        ),

        "has_gitignore": overview.get(
            ".gitignore",
            False,
        ),

        
        # GitHub metadata
        

        "language": github_data.get(
            "language",
            "",
        ),

        "size": github_data.get(
            "size",
            0,
        ),

        "created_days": github_data.get(
            "created_days",
            0,
        ),

        "updated_days": github_data.get(
            "updated_days",
            0,
        ),

        
        # Metric-support indicators
        

        "complexity_supported": (
            complexity_value is not None
            and complexity_value != "Not Supported"
            and complexity_value != "-"
        ),

        "functions_supported": (
            functions_value is not None
            and functions_value != "Not Supported"
            and functions_value != "-"
        ),
    }


# HOME

@app.route("/")
def home():
    return render_template(
        "index.html"
    )


# ANALYZE REPOSITORY

@app.route(
    "/analyze",
    methods=["POST"],
)
def analyze():

    global LAST_CONTEXT

    start_time = time.time()

    repo_url = request.form.get(
        "repo_url",
        "",
    ).strip()

    # Validate URL

    if not validate_github_url(
        repo_url
    ):

        return render_template(
            "index.html",
            error=(
                "Please enter a valid "
                "GitHub repository URL."
            ),
        )

    # GitHub API

    github_data = get_github_data(
        repo_url
    )

    if github_data is None:

        return render_template(
            "index.html",
            error=(
                "Could not retrieve "
                "repository information "
                "from GitHub."
            ),
        )

    print(
        "✅ GitHub API Done"
    )

    # Clone repository

    success, result = clone_repository(
        repo_url
    )

    if not success:

        return render_template(
            "index.html",
            error=result,
        )

    repo_path = result

    print(
        "✅ Clone Done"
    )

    # Repository analyzers

    repo_info = repository_information(
        repo_path
    )

    overview = get_repository_overview(
        repo_path
    )

    languages = detect_languages(
        repo_path
    )

    tech = detect_tech_stack(
        repo_path
    )

    dependencies = analyze_dependencies(
        repo_path
    )

    statistics = repository_statistics(
        repo_path
    )

    complexity = analyze_complexity(
        repo_path
    )

    readme = analyze_readme(
        repo_path
    )

    print(
        "✅ Repository analysis complete"
    )

    # AI summary

    ai_summary = generate_ai_summary(
        overview,
        languages,
        tech,
        statistics,
        readme,
        complexity,
        dependencies,
    )

    # Build ML feature vector

    ml_features = build_ml_features(
        github_data=github_data,
        statistics=statistics,
        overview=overview,
        readme=readme,
        dependencies=dependencies,
        complexity=complexity,
        languages=languages,
        tech=tech,
    )

    print(
        "✅ ML feature vector created"
    )

    # ML classification

    try:

        health_prediction = (
            predict_health_details(
                ml_features
            )
        )

        print(
            "✅ ML Health Prediction:",
            health_prediction,
        )

    except Exception as exc:

        print(
            "❌ ML prediction failed:",
            exc,
        )

        return render_template(
            "index.html",
            error=(
                "Repository analysis completed, "
                "but ML health prediction failed."
            ),
        )

    # AUTHORITATIVE BASELINE HEALTH SCORE
    #
    # This is calculated from the CURRENT health_score.py implementation.
    # It is separate from the ML classification result.

    baseline_features = {

        "readme_score": readme.get(
            "score",
            0,
        ),

        "has_readme": overview.get(
            "README",
            False,
        ),

        "has_license": overview.get(
            "License",
            False,
        ),

        "has_gitignore": overview.get(
            ".gitignore",
            False,
        ),

        "complexity": complexity.get(
            "complexity",
            None,
        ),

        "dependency_count": len(
            dependencies
        ),

        "updated_days": github_data.get(
            "updated_days",
            0,
        ),

        "total_files": statistics.get(
            "total_files",
            0,
        ),

        "total_folders": statistics.get(
            "total_folders",
            0,
        ),

        "lines": statistics.get(
            "lines",
            0,
        ),

        "functions": complexity.get(
            "functions",
            None,
        ),
    }

    baseline_health_score = (
        calculate_health_score(
            baseline_features
        )
    )

    baseline_health_grade = (
        classify_health(
            baseline_health_score
        )
    )

    print(
        "✅ Baseline Health Score:",
        baseline_health_score,
    )

    print(
        "✅ Baseline Health Grade:",
        baseline_health_grade,
    )

    # Store the authoritative baseline score in the summary.
    #
    # This replaces the old simplified score generated by summary_generator.

    ai_summary["health_score"] = (
        baseline_health_score
    )

    ai_summary["baseline_health_grade"] = (
        baseline_health_grade
    )

    # Store ML grade separately.

    ai_summary["health_grade"] = (
        health_prediction["grade"]
    )

    # Save context

    end_time = time.time()

    print(
        f"Analysis completed in "
        f"{end_time - start_time:.2f} seconds"
    )

    LAST_CONTEXT = {

        "repo": repo_info,

        "github_data": github_data,

        "overview": overview,

        "languages": languages,

        "tech": tech,

        "readme": readme,

        "dependencies": dependencies,

        "statistics": statistics,

        "complexity": complexity,

        "ai_summary": ai_summary,

        "repo_path": repo_path,

        # ML data

        "ml_features": ml_features,

        "health_prediction": health_prediction,

        # Explicit baseline data

        "baseline_health_score": (
            baseline_health_score
        ),

        "baseline_health_grade": (
            baseline_health_grade
        ),
    }

    # Redirect to dashboard

    return redirect(
        url_for("dashboard")
    )


# DASHBOARD

@app.route(
    "/dashboard"
)
def dashboard():

    context = (
        get_context_or_redirect()
    )

    if context is None:

        return redirect(
            url_for("home")
        )

    return render_template(
        "dashboard.html",
        **context,
    )


# SUMMARY

@app.route(
    "/summary"
)
def summary():

    context = (
        get_context_or_redirect()
    )

    if context is None:

        return redirect(
            url_for("home")
        )

    return render_template(
        "summary.html",
        **context,
    )


# HEALTH

@app.route(
    "/health"
)
def health():

    context = (
        get_context_or_redirect()
    )

    if context is None:

        return redirect(
            url_for("home")
        )

    return render_template(
        "health.html",
        **context,
    )


# ARCHITECTURE

@app.route(
    "/architecture"
)
def architecture():

    context = (
        get_context_or_redirect()
    )

    if context is None:

        return redirect(
            url_for("home")
        )

    return render_template(
        "architecture.html",
        **context,
    )


# SECURITY

@app.route(
    "/security"
)
def security():

    context = (
        get_context_or_redirect()
    )

    if context is None:

        return redirect(
            url_for("home")
        )

    return render_template(
        "security.html",
        **context,
    )


# TECH STACK

@app.route(
    "/tech"
)
def tech():

    context = (
        get_context_or_redirect()
    )

    if context is None:

        return redirect(
            url_for("home")
        )

    return render_template(
        "tech.html",
        **context,
    )


# AI CHAT

@app.route(
    "/chat"
)
def chat():

    context = (
        get_context_or_redirect()
    )

    if context is None:

        return redirect(
            url_for("home")
        )

    return render_template(
        "chat.html",
        **context,
    )


# RUN APPLICATION

if __name__ == "__main__":

    app.run(
        debug=True,use_reloader = False
    )