import os
import re
from radon.complexity import cc_visit


def analyze_complexity(repo_path):
    total_complexity = 0
    total_functions = 0
    detected_languages = set()

    # Java method regex
    java_method_pattern = re.compile(
        r'(public|private|protected)?\s+'
        r'(static\s+)?'
        r'[\w<>\[\]]+\s+'
        r'\w+\s*\([^)]*\)\s*\{'
    )

    # JavaScript / TypeScript function regex
    js_function_pattern = re.compile(
        r'function\s+\w+\s*\('
        r'|const\s+\w+\s*=\s*\(?.*?\)?\s*=>'
        r'|let\s+\w+\s*=\s*\(?.*?\)?\s*=>'
        r'|var\s+\w+\s*=\s*\(?.*?\)?\s*=>'
        r'|async\s+function\s+\w+\s*\('
    )

    # React Component regex
    react_component_pattern = re.compile(
        r'function\s+[A-Z]\w*\s*\('
        r'|const\s+[A-Z]\w*\s*=\s*\('
    )

    for root, dirs, files in os.walk(repo_path):

        if ".git" in dirs:
            dirs.remove(".git")

        for file in files:

            filepath = os.path.join(root, file)

            # -----------------------
            # Python
            # -----------------------
            if file.endswith(".py"):

                detected_languages.add("Python")

                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        source = f.read()

                    results = cc_visit(source)

                    for item in results:
                        total_complexity += item.complexity
                        total_functions += 1

                except Exception:
                    pass

            # -----------------------
            # Java
            # -----------------------
            elif file.endswith(".java"):

                detected_languages.add("Java")

                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        source = f.read()

                    methods = java_method_pattern.findall(source)

                    total_functions += len(methods)

                    complexity_keywords = (
                        source.count("if")
                        + source.count("for")
                        + source.count("while")
                        + source.count("switch")
                        + source.count("catch")
                        + source.count("&&")
                        + source.count("||")
                    )

                    total_complexity += max(
                        len(methods),
                        complexity_keywords
                    )

                except Exception:
                    pass

            # -----------------------
            # JavaScript / React / TypeScript
            # -----------------------
            elif file.endswith((".js", ".jsx", ".ts", ".tsx")):

                detected_languages.add("JavaScript")

                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        source = f.read()

                    functions = js_function_pattern.findall(source)
                    components = react_component_pattern.findall(source)

                    count = len(functions) + len(components)

                    total_functions += count

                    complexity_keywords = (
                        source.count("if")
                        + source.count("for")
                        + source.count("while")
                        + source.count("switch")
                        + source.count("catch")
                        + source.count("&&")
                        + source.count("||")
                    )

                    total_complexity += max(count, complexity_keywords)

                except Exception:
                    pass

            # -----------------------
            # Other Languages
            # -----------------------
            elif file.endswith(".cpp"):
                detected_languages.add("C++")

            elif file.endswith(".c"):
                detected_languages.add("C")

            elif file.endswith(".go"):
                detected_languages.add("Go")

            elif file.endswith(".rs"):
                detected_languages.add("Rust")

            elif file.endswith(".php"):
                detected_languages.add("PHP")

            elif file.endswith(".kt"):
                detected_languages.add("Kotlin")

            elif file.endswith(".swift"):
                detected_languages.add("Swift")

    # -----------------------
    # Final Result
    # -----------------------

    if total_functions > 0:

        average = round(total_complexity / total_functions, 2)

        return {
            "functions": total_functions,
            "complexity": average,
            "supported": True,
            "language": ", ".join(sorted(detected_languages))
        }

    # Unsupported Language
    if detected_languages:

        return {
            "functions": "-",
            "complexity": "Not Supported",
            "supported": False,
            "language": ", ".join(sorted(detected_languages))
        }

    # Empty Repository
    return {
        "functions": 0,
        "complexity": 0,
        "supported": False,
        "language": "Unknown"
    }