import os
import sys

import pandas as pd

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../..",
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from analyzer.health_score import (
    calculate_health_score,
    classify_health,
)


INPUT_FILE = os.path.join(
    PROJECT_ROOT,
    "ml",
    "data",
    "repository_dataset.csv",
)


def main():
    df = pd.read_csv(INPUT_FILE)

    scores = df.apply(
        lambda row: calculate_health_score(
            row.to_dict()
        ),
        axis=1,
    )

    df["health_score"] = scores

    df["health_grade"] = df[
        "health_score"
    ].apply(classify_health)

    df.to_csv(
        INPUT_FILE,
        index=False,
    )

    print()
    print("=" * 60)
    print("HEALTH LABEL GENERATION")
    print("=" * 60)

    print(
        f"Repositories: {len(df)}"
    )

    print()

    print(
        df[
            [
                "repository",
                "health_score",
                "health_grade",
            ]
        ].to_string(index=False)
    )

    print()
    print("Grade distribution:")
    print(
        df["health_grade"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    print()
    print(
        "Score statistics:"
    )

    print(
        df["health_score"]
        .describe()
        .to_string()
    )


if __name__ == "__main__":
    main()