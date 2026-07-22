import os


def detect_tech_stack(repo_path):

    technologies = []

    for root, dirs, files in os.walk(repo_path):

        for file in files:

            filename = file.lower()

            # Python
            if filename.endswith(".py"):
                technologies.append("Python")

                # GUI / Visualization Libraries
                path = os.path.join(root, file)

                with open(path, "r", encoding="utf-8", errors="ignore") as python_file:

                    content = python_file.read()

                    if "tkinter" in content:
                        technologies.append("Tkinter GUI")

                    if "matplotlib" in content:
                        technologies.append("Matplotlib")

                    if "numpy" in content:
                        technologies.append("NumPy")

            # JavaScript
            if filename.endswith(".js"):
                technologies.append("JavaScript")

            # Java
            if filename.endswith(".java"):
                technologies.append("Java")

            # React / Node.js
            if filename == "package.json":
                technologies.append("Node.js")

            # Docker
            if filename == "dockerfile":
                technologies.append("Docker")

            # Django
            if filename == "manage.py":
                technologies.append("Django")

            # Flask
            if filename == "app.py":
                technologies.append("Flask")


    return list(set(technologies))