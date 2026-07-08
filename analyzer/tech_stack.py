import os


def detect_tech_stack(repo_path):

    technologies = []

    for root, dirs, files in os.walk(repo_path):

        for file in files:

            filename = file.lower()

            if filename == "requirements.txt":
                technologies.append("Python")

            if filename == "package.json":
                technologies.append("Node.js")

            if filename == "dockerfile":
                technologies.append("Docker")

            if filename == "pom.xml":
                technologies.append("Java")

            if filename == "manage.py":
                technologies.append("Django")

            if filename == "app.py":
                technologies.append("Flask")

    return list(set(technologies))