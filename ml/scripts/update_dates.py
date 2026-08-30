import os
import sys
import csv
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

CSV_FILE = os.path.join(
    PROJECT_ROOT,
    "ml",
    "data",
    "repository_dataset.csv"
)

load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

TOKEN = os.getenv("GITHUB_TOKEN")

if not TOKEN:
    raise RuntimeError("GITHUB_TOKEN not found in .env")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


def get_dates(repo):
    url = f"https://api.github.com/repos/{repo}"

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=20
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"GitHub API {response.status_code}: "
            f"{response.text[:200]}"
        )

    data = response.json()

    created = datetime.strptime(
        data["created_at"],
        "%Y-%m-%dT%H:%M:%SZ"
    ).replace(tzinfo=timezone.utc)

    updated = datetime.strptime(
        data["updated_at"],
        "%Y-%m-%dT%H:%M:%SZ"
    ).replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)

    created_days = round(
        (now - created).total_seconds() / 86400,
        2
    )

    updated_days = round(
        (now - updated).total_seconds() / 86400,
        2
    )

    return created_days, updated_days


def main():
    with open(
        CSV_FILE,
        "r",
        newline="",
        encoding="utf-8"
    ) as f:
        rows = list(csv.DictReader(f))

    print(f"Updating dates for {len(rows)} repositories...\n")

    success = 0
    failed = 0

    for index, row in enumerate(rows, start=1):

        repo = row["repository"]

        try:
            created_days, updated_days = get_dates(repo)

            row["created_days"] = created_days
            row["updated_days"] = updated_days

            success += 1

            print(
                f"[{index}/{len(rows)}] "
                f"{repo} → "
                f"updated_days={updated_days}"
            )

        except Exception as exc:
            failed += 1
            print(
                f"[{index}/{len(rows)}] "
                f"FAILED {repo}: {exc}"
            )

    # Rewrite the existing CSV with updated values
    fieldnames = rows[0].keys()

    with open(
        CSV_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(rows)

    print("\n" + "=" * 60)
    print("DATE UPDATE COMPLETE")
    print("=" * 60)
    print(f"Successful: {success}")
    print(f"Failed:     {failed}")
    print(f"Updated:    {CSV_FILE}")


if __name__ == "__main__":
    main()