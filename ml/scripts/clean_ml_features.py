from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "repository_dataset.csv"
)


def main():
    df = pd.read_csv(DATA_FILE)

    print("=" * 70)
    print("CLEANING ML FEATURES")
    print("=" * 70)

    # ------------------------------------------------------------
    # Preserve whether these metrics were actually available
    # ------------------------------------------------------------

    df["complexity_supported"] = (
        pd.to_numeric(
            df["complexity"],
            errors="coerce",
        ).notna()
    )

    df["functions_supported"] = (
        pd.to_numeric(
            df["functions"],
            errors="coerce",
        ).notna()
    )

    # ------------------------------------------------------------
    # Convert numeric columns to actual numeric values
    # ------------------------------------------------------------

    numeric_columns = [
        "total_files",
        "total_folders",
        "lines",
        "python",
        "html",
        "css",
        "javascript",
        "java",
        "cpp",
        "dependency_count",
        "readme_score",
        "functions",
        "complexity",
        "language_count",
        "tech_stack_count",
        "stars",
        "forks",
        "watchers",
        "open_issues",
        "size",
        "created_days",
        "updated_days",
        "health_score",
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            )

    # ------------------------------------------------------------
    # Show missing values created by conversion
    # ------------------------------------------------------------

    print("\nMissing values after conversion:")

    missing = df.isna().sum()
    missing = missing[missing > 0].sort_values(
        ascending=False
    )

    if len(missing) == 0:
        print("None")
    else:
        print(missing.to_string())

    # ------------------------------------------------------------
    # Save cleaned dataset
    # ------------------------------------------------------------

    df.to_csv(
        DATA_FILE,
        index=False,
    )

    print()
    print("Dataset cleaned successfully.")
    print(f"Rows    : {len(df)}")
    print(f"Columns : {len(df.columns)}")
    print(f"Saved   : {DATA_FILE}")


if __name__ == "__main__":
    main()