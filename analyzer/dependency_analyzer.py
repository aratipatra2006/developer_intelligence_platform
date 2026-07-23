import os
import json
import xml.etree.ElementTree as ET


def analyze_dependencies(repo_path):

    dependencies = []

    # -------------------------------
    # Python (requirements.txt)
    # -------------------------------

    req = os.path.join(repo_path, "requirements.txt")

    if os.path.exists(req):

        with open(req, "r", encoding="utf-8", errors="ignore") as file:

            for line in file:

                line = line.strip()

                if line and not line.startswith("#"):

                    dependency = line.split("==")[0].split(">=")[0]

                    dependencies.append(dependency)

    # -------------------------------
    # JavaScript (package.json)
    # -------------------------------

    # -------------------------------
# JavaScript (package.json)
# -------------------------------

    for root, dirs, files in os.walk(repo_path):

     if "package.json" in files:

        package = os.path.join(root, "package.json")

        try:
            with open(package, "r", encoding="utf-8") as file:

                data = json.load(file)

                # Regular dependencies
                if "dependencies" in data:
                    dependencies.extend(data["dependencies"].keys())

                # Development dependencies
                if "devDependencies" in data:
                    dependencies.extend(data["devDependencies"].keys())

        except Exception as e:
            print(f"Error reading {package}: {e}")

    # -------------------------------
    # Java (pom.xml)
    # -------------------------------

    pom = os.path.join(repo_path, "pom.xml")

    if os.path.exists(pom):

        tree = ET.parse(pom)

        root = tree.getroot()

        for dependency in root.findall(".//{*}artifactId"):

            dependencies.append(dependency.text)

    # -------------------------------
    # Python Import Detection
    # -------------------------------

    for root, dirs, files in os.walk(repo_path):

        for file in files:

            if file.endswith(".py"):

                path = os.path.join(root, file)

                with open(path, "r", encoding="utf-8", errors="ignore") as python_file:

                    content = python_file.read()

                    if "import tkinter" in content:
                        dependencies.append("tkinter")

                    if "import matplotlib" in content:
                        dependencies.append("matplotlib")

                    if "import numpy" in content:
                        dependencies.append("numpy")

                    if "import pandas" in content:
                        dependencies.append("pandas")    

    # Remove duplicates

    dependencies = sorted(set(dependencies))

    return dependencies