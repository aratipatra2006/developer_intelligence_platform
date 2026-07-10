from flask import Flask, render_template, request

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
import time
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
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

    languages = detect_languages(repo_path)

    tech = detect_tech_stack(repo_path)
    dependencies = analyze_dependencies(repo_path)
    statistics = repository_statistics(repo_path)
    complexity = analyze_complexity(repo_path)
    readme = analyze_readme(repo_path)
  
    end_time = time.time()

    print(f"Analysis completed in {end_time - start_time:.2f} seconds")
    return render_template(

    "dashboard.html",

    repo=repo_info,

    overview=overview,

    languages=languages,

    tech=tech,
    readme=readme,
    dependencies=dependencies,
    statistics=statistics,
    complexity=complexity,
    repo_path=repo_path

)

if __name__=="__main__":
    app.run(debug=True)