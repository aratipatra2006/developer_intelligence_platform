from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUTPUT_FILE = ROOT / "project_structure.txt"

# Directories to completely ignore
EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    ".idea",
    ".vscode",
    "repositories",
    "uploads",
    "logs",
    "tmp",
    "temp",
    "_clean_project",
}

# Files to ignore
EXCLUDED_FILES = {
    ".env",
    "project_structure.txt",
    "developer_intelligence_platform_clean.zip",
}


def should_skip(path: Path) -> bool:
    if path.is_dir() and path.name in EXCLUDED_DIRS:
        return True

    if path.is_file() and path.name in EXCLUDED_FILES:
        return True

    return False


def build_tree(directory: Path, prefix: str = "") -> list[str]:
    lines = []

    # Filter before recursion
    items = [
        item
        for item in directory.iterdir()
        if not should_skip(item)
    ]

    items.sort(key=lambda p: (p.is_file(), p.name.lower()))

    for index, item in enumerate(items):
        is_last = index == len(items) - 1

        connector = "└── " if is_last else "├── "
        lines.append(f"{prefix}{connector}{item.name}")

        if item.is_dir():
            extension = "    " if is_last else "│   "
            lines.extend(
                build_tree(item, prefix + extension)
            )

    return lines


def main():
    lines = [f"{ROOT.name}/"]
    lines.extend(build_tree(ROOT))

    structure = "\n".join(lines)

    OUTPUT_FILE.write_text(
        structure,
        encoding="utf-8"
    )

    print(f"Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()