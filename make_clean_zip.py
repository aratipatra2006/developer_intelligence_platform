from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parent
STAGING = ROOT / "_clean_project"

ZIP_NAME = "developer_intelligence_platform_clean.zip"
STRUCTURE_NAME = "project_structure.txt"

# Entire directories to exclude from the submission
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

# Files to exclude
EXCLUDED_FILES = {
    ".env",
    ZIP_NAME,
    STRUCTURE_NAME,
}

# Skip files larger than this unless explicitly required
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def should_skip(path: Path) -> bool:
    relative = path.relative_to(ROOT)

    # Skip anything inside an excluded directory
    if any(part in EXCLUDED_DIRS for part in relative.parts):
        return True

    # Skip known files
    if path.name in EXCLUDED_FILES:
        return True

    # Skip generated Python bytecode
    if path.suffix.lower() in {".pyc", ".pyo"}:
        return True

    # Skip unusually large files
    try:
        if path.is_file() and path.stat().st_size > MAX_FILE_SIZE:
            print(f"Skipping large file: {relative}")
            return True
    except OSError:
        return True

    return False


def copy_project():
    if STAGING.exists():
        shutil.rmtree(STAGING)

    STAGING.mkdir()

    copied = 0
    skipped = 0

    def copy_directory(src: Path, dst: Path):
        nonlocal copied, skipped

        for item in src.iterdir():

            # Skip excluded directories BEFORE entering them
            if item.is_dir():
                if item.name in EXCLUDED_DIRS:
                    print(f"Skipping directory: {item.relative_to(ROOT)}")
                    skipped += 1
                    continue

                copy_directory(item, dst / item.name)

            elif item.is_file():
                if should_skip(item):
                    skipped += 1
                    continue

                destination = dst / item.name
                destination.parent.mkdir(parents=True, exist_ok=True)

                shutil.copy2(item, destination)
                copied += 1

    copy_directory(ROOT, STAGING)

    print()
    print(f"Copied : {copied} files")
    print(f"Skipped: {skipped} files")


def generate_structure():
    lines = [f"{ROOT.name}/"]

    def walk(directory: Path, prefix=""):
        items = sorted(
            directory.iterdir(),
            key=lambda p: (p.is_file(), p.name.lower())
        )

        for index, item in enumerate(items):
            last = index == len(items) - 1
            connector = "└── " if last else "├── "

            lines.append(f"{prefix}{connector}{item.name}")

            if item.is_dir():
                extension = "    " if last else "│   "
                walk(item, prefix + extension)

    walk(STAGING)

    structure = "\n".join(lines)

    # Save next to the ZIP
    (ROOT / STRUCTURE_NAME).write_text(
        structure,
        encoding="utf-8"
    )

    # Also include it inside the ZIP
    (STAGING / STRUCTURE_NAME).write_text(
        structure,
        encoding="utf-8"
    )


def create_zip():
    zip_path = ROOT / ZIP_NAME

    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(
        zip_path,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as z:
        for file in STAGING.rglob("*"):
            if file.is_file():
                z.write(
                    file,
                    file.relative_to(STAGING)
                )

    return zip_path


def main():
    print("=" * 60)
    print("Creating clean project submission")
    print("=" * 60)

    copy_project()
    generate_structure()

    zip_path = create_zip()

    # Remove temporary staging folder
    shutil.rmtree(STAGING)

    print()
    print("=" * 60)
    print("DONE")
    print("=" * 60)

    print(f"ZIP : {zip_path}")
    print(f"TXT : {ROOT / STRUCTURE_NAME}")

    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"ZIP size: {size_mb:.2f} MB")


if __name__ == "__main__":
    main()