from flask import Flask, render_template, request

from analyzer.clone_repo import clone_repository
from analyzer.repo_info import repository_information
from analyzer.language_detector import detect_languages
from analyzer.tech_stack import detect_tech_stack
from utils.validators import validate_github_url
from analyzer.repository_overview import get_repository_overview

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():

    repo_url = request.form["repo_url"]

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
    if not validate_github_url(repo_url):

       return render_template(
        "index.html",
        error="Please enter a valid GitHub repository URL."
      )

    return render_template(

    "dashboard.html",

    repo=repo_info,

    overview=overview,

    languages=languages,

    tech=tech,

    repo_path=repo_path

)

if __name__=="__main__":
    app.run(debug=True)