import os
from collections import Counter


extensions = {

    # Python
    ".py": "Python",

    # Java
    ".java": "Java",

    # JavaScript / TypeScript
    ".js": "JavaScript",
    ".jsx": "React JSX",
    ".ts": "TypeScript",
    ".tsx": "React TSX",

    # C Family
    ".c": "C",
    ".cpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".h": "C/C++ Header",
    ".hpp": "C++ Header",

    # C#
    ".cs": "C#",

    # Go
    ".go": "Go",

    # Rust
    ".rs": "Rust",

    # Kotlin
    ".kt": "Kotlin",

    # Swift
    ".swift": "Swift",

    # PHP
    ".php": "PHP",

    # Ruby
    ".rb": "Ruby",

    # Dart
    ".dart": "Dart",

    # R
    ".r": "R",

    # MATLAB
    ".m": "MATLAB",

    # Scala
    ".scala": "Scala",

    # Perl
    ".pl": "Perl",

    # Shell
    ".sh": "Shell",
    ".bash": "Bash",

    # HTML / CSS
    ".html": "HTML",
    ".htm": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".sass": "SASS",
    ".less": "LESS",

    # SQL
    ".sql": "SQL",

    # XML / JSON / YAML
    ".xml": "XML",
    ".json": "JSON",
    ".yaml": "YAML",
    ".yml": "YAML",

    # Markdown
    ".md": "Markdown",

    # Docker
    ".dockerfile": "Docker",

    # Vue
    ".vue": "Vue.js",

    # Svelte
    ".svelte": "Svelte",

    # Angular
    ".component": "Angular",

    # Configuration
    ".ini": "INI",
    ".toml": "TOML",
    ".env": "Environment File",

    # Notebook
    ".ipynb": "Jupyter Notebook",

    # Text
    ".txt": "Text"
}


def detect_languages(repo_path):

    counter = Counter()

    for root, dirs, files in os.walk(repo_path):

       for file in files:

    # Detect files without extensions
         if file == "Dockerfile":
          counter["Docker"] += 1
          continue

         if file == "Makefile":
          counter["Makefile"] += 1
          continue

         ext = os.path.splitext(file)[1].lower()

         if ext in extensions:
          counter[extensions[ext]] += 1

    return dict(counter)