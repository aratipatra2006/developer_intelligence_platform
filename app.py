from flask import Flask, render_template, request, redirect, url_for

from analyzer.clone_repo import clone_repository
from analyzer.repo_info import repository_information
from analyzer.language_detector import detect_languages
from analyzer.tech_stack import detect_tech_stack
from utils.validators import validate_github_url
from analyzer.repository_overview import get_repository_overview
from analyzer.repository_statistics import repository_statistics
from analyzer.readme_analyzer import analyze_readme
from analyzer.dependency_analyzer import analyze_dependencies
from analyzer.complexity_analyzer import analyze_complexity
from ai.summary_generator import generate_ai_summary

import time

app = Flask(__name__)
app.secret_key = "developer_intelligence"

# Holds the most recently completed analysis so the standalone feature pages
# (summary, health, architecture, security, tech, chat) can render it via a
# plain GET request without re-cloning/re-analyzing the repo.
# NOTE: this is process-wide, in-memory state — fine for a single-user local
# app, but if this ever runs with multiple workers/users at once, swap this
# for a per-session store (e.g. flask.session, or a keyed cache by repo_url).
LAST_CONTEXT = None


def get_context_or_redirect():
    """Returns the last analysis context, or None if nothing's been analyzed yet."""
    return LAST_CONTEXT


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    global LAST_CONTEXT

    start_time = time.time()
    repo_url = request.form["repo_url"]
    if not validate_github_url(repo_url):
        return render_template(
            "index.html",
            error="Please enter a valid GitHub repository URL."
        )

    success, result = clone_repository(repo_url)
    if not success:
        return render_template(
            "index.html",
            error=result
        )
    repo_path = result
    repo_info = repository_information(repo_path)
    overview = get_repository_overview(repo_path)
    print("OVERVIEW:", overview)

    languages = detect_languages(repo_path)

    tech = detect_tech_stack(repo_path)
    dependencies = analyze_dependencies(repo_path)
    statistics = repository_statistics(repo_path)
    complexity = analyze_complexity(repo_path)
    readme = analyze_readme(repo_path)

    ai_summary = generate_ai_summary(
        overview,
        languages,
        tech,
        statistics,
        readme,
        complexity,
        dependencies
    )
    print(ai_summary)

    end_time = time.time()
    print(f"Analysis completed in {end_time - start_time:.2f} seconds")

    LAST_CONTEXT = dict(
        repo=repo_info,
        overview=overview,
        languages=languages,
        tech=tech,
        readme=readme,
        dependencies=dependencies,
        statistics=statistics,
        complexity=complexity,
        ai_summary=ai_summary,
        repo_path=repo_path,
    )

    # Redirect (not render) so a page refresh doesn't resubmit the form,
    # and so /summary, /health, etc. all have somewhere to pull data from.
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard():
    context = get_context_or_redirect()
    if context is None:
        return redirect(url_for("home"))
    return render_template("dashboard.html", **context)


@app.route("/summary")
def summary():
    context = get_context_or_redirect()
    if context is None:
        return redirect(url_for("home"))

    print(context.keys())     

    return render_template("summary.html", **context)

@app.route("/health")
def health():
    context = get_context_or_redirect()
    if context is None:
        return redirect(url_for("home"))
    return render_template("health.html", **context)


@app.route("/architecture")
def architecture():
    context = get_context_or_redirect()
    if context is None:
        return redirect(url_for("home"))
    return render_template("architecture.html", **context)


@app.route("/security")
def security():
    context = get_context_or_redirect()
    if context is None:
        return redirect(url_for("home"))
    return render_template("security.html", **context)


@app.route("/tech")
def tech():
    context = get_context_or_redirect()
    if context is None:
        return redirect(url_for("home"))
    return render_template("tech.html", **context)


@app.route("/chat")
def chat():
    context = get_context_or_redirect()
    if context is None:
        return redirect(url_for("home"))
    return render_template("chat.html", **context)


if __name__ == "__main__":
    app.run(debug=True)