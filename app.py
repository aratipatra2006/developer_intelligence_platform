from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():

    repo_url = request.form["repo_url"]

    print(repo_url)

    return f"""
    Repository Received Successfully

    <br><br>

    {repo_url}
    """

if __name__ == "__main__":
    app.run(debug=True)