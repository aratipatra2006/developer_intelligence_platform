from __future__ import annotations

import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


if not GITHUB_TOKEN:
    raise RuntimeError(
        "GITHUB_TOKEN not found in .env"
    )


HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


API_URL = "https://api.github.com/search/repositories"


ROOT = Path(__file__).resolve().parents[2]

OUTPUT_FILE = (
    ROOT
    / "ml"
    / "dataset"
    / "repositories.txt"
)


# Number of NEW repositories we want.
TARGET_NEW_REPOSITORIES = 500


# GitHub returns at most 100 results per request.
PER_PAGE = 100


# Search queries.
#
# Using multiple languages and star ranges produces a more
# diverse dataset instead of only collecting huge popular repos.
QUERIES = [

    # Java
    "language:Java stars:10..1000",
    "language:Java stars:1001..10000",
    "language:Java stars:10001..50000",

    # JavaScript
    "language:JavaScript stars:10..1000",
    "language:JavaScript stars:1001..10000",
    "language:JavaScript stars:10001..50000",

    # TypeScript
    "language:TypeScript stars:10..1000",
    "language:TypeScript stars:1001..10000",
    "language:TypeScript stars:10001..50000",

    # C++
    "language:C++ stars:10..1000",
    "language:C++ stars:1001..10000",
    "language:C++ stars:10001..50000",

    # C
    "language:C stars:10..1000",
    "language:C stars:1001..10000",
    "language:C stars:10001..50000",

    # Go
    "language:Go stars:10..1000",
    "language:Go stars:1001..10000",
    "language:Go stars:10001..50000",

    # Rust
    "language:Rust stars:10..1000",
    "language:Rust stars:1001..10000",
    "language:Rust stars:10001..50000",

    # Kotlin
    "language:Kotlin stars:10..1000",
    "language:Kotlin stars:1001..10000",
    "language:Kotlin stars:10001..50000",

    # PHP
    "language:PHP stars:10..1000",
    "language:PHP stars:1001..10000",
    "language:PHP stars:10001..50000",

    # Ruby
    "language:Ruby stars:10..1000",
    "language:Ruby stars:1001..10000",
    "language:Ruby stars:10001..50000",

    # Swift
    "language:Swift stars:10..1000",
    "language:Swift stars:1001..10000",
    "language:Swift stars:10001..50000",
]


# ============================================================
# HELPERS
# ============================================================

def normalize_repo(repo: str) -> str:
    """
    Normalize repository identifier into owner/repo format.
    """

    repo = repo.strip()

    repo = repo.replace(
        "https://github.com/",
        "",
    )

    repo = repo.replace(
        "http://github.com/",
        "",
    )

    repo = repo.strip("/")

    if repo.endswith(".git"):
        repo = repo[:-4]

    return repo.lower()


def load_existing_repositories() -> set[str]:
    """
    Load existing repositories from repositories.txt.
    """

    existing = set()

    if not OUTPUT_FILE.exists():
        return existing

    with open(
        OUTPUT_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        for line in file:

            line = line.strip()

            if not line:
                continue

            existing.add(
                normalize_repo(line)
            )

    return existing


def get_rate_limit():
    """
    Get current GitHub search/core rate limits.
    """

    response = requests.get(
        "https://api.github.com/rate_limit",
        headers=HEADERS,
        timeout=30,
    )

    if response.status_code != 200:
        return None

    return response.json()


def search_repositories(
    query: str,
    page: int,
):
    """
    Search GitHub repositories.
    """

    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": PER_PAGE,
        "page": page,
    }

    while True:

        response = requests.get(
            API_URL,
            headers=HEADERS,
            params=params,
            timeout=30,
        )

        # ----------------------------------------------------
        # Success
        # ----------------------------------------------------

        if response.status_code == 200:
            return response.json()

        # ----------------------------------------------------
        # Rate limit
        # ----------------------------------------------------

        if response.status_code in {
            403,
            429,
        }:

            print(
                "⚠️ GitHub rate limit reached."
            )

            rate_info = get_rate_limit()

            if rate_info:

                search_limit = (
                    rate_info
                    .get("resources", {})
                    .get("search", {})
                )

                remaining = (
                    search_limit
                    .get("remaining")
                )

                reset = (
                    search_limit
                    .get("reset")
                )

                print(
                    f"Search remaining: {remaining}"
                )

                if reset:

                    current_time = time.time()

                    wait_seconds = max(
                        1,
                        int(
                            reset
                            - current_time
                            + 5
                        )
                    )

                    print(
                        f"Waiting {wait_seconds} seconds..."
                    )

                    time.sleep(
                        wait_seconds
                    )

                    continue

            print(
                "Unable to determine reset time."
            )

            return None

        # ----------------------------------------------------
        # Other errors
        # ----------------------------------------------------

        print(
            f"GitHub API error "
            f"{response.status_code}: "
            f"{response.text[:300]}"
        )

        return None


# ============================================================
# MAIN COLLECTION
# ============================================================

def main():

    print("=" * 70)
    print("GITHUB REPOSITORY URL COLLECTOR")
    print("=" * 70)

    # --------------------------------------------------------
    # Existing repositories
    # --------------------------------------------------------

    existing = (
        load_existing_repositories()
    )

    print(
        f"Existing repositories: "
        f"{len(existing)}"
    )

    print(
        f"Target NEW repositories: "
        f"{TARGET_NEW_REPOSITORIES}"
    )

    print()

    collected = []

    collected_set = set()

    # --------------------------------------------------------
    # Search
    # --------------------------------------------------------

    for query_index, query in enumerate(
        QUERIES,
        start=1,
    ):

        if len(collected) >= TARGET_NEW_REPOSITORIES:
            break

        print(
            f"[Query {query_index}/{len(QUERIES)}]"
        )

        print(
            f"Search: {query}"
        )

        print()

        for page in range(1, 11):

            if len(collected) >= TARGET_NEW_REPOSITORIES:
                break

            print(
                f"  Page {page}"
            )

            data = search_repositories(
                query,
                page,
            )

            if not data:
                print(
                    "  No response."
                )
                break

            items = data.get(
                "items",
                [],
            )

            if not items:
                print(
                    "  No more repositories."
                )
                break

            added_this_page = 0

            for repo in items:

                # ------------------------------------------------
                # Basic repository filters
                # ------------------------------------------------

                if repo.get(
                    "fork",
                    False,
                ):
                    continue

                if repo.get(
                    "archived",
                    False,
                ):
                    continue

                full_name = repo.get(
                    "full_name"
                )

                if not full_name:
                    continue

                normalized = (
                    normalize_repo(
                        full_name
                    )
                )

                # Existing dataset?
                if normalized in existing:
                    continue

                # Already collected during this run?
                if normalized in collected_set:
                    continue

                collected_set.add(
                    normalized
                )

                collected.append(
                    f"https://github.com/{full_name}"
                )

                added_this_page += 1

                if len(collected) >= TARGET_NEW_REPOSITORIES:
                    break

            print(
                f"  Added: {added_this_page}"
            )

            print(
                f"  Total new: "
                f"{len(collected)}"
                f"/{TARGET_NEW_REPOSITORIES}"
            )

            # Avoid unnecessary requests.
            if len(items) < PER_PAGE:
                break

            # Small delay between search requests.
            time.sleep(1)

        print()

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    if not collected:

        print(
            "No new repositories collected."
        )

        return

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Append to existing file.
    with open(
        OUTPUT_FILE,
        "a",
        encoding="utf-8",
    ) as file:

        for repo in collected:

            file.write(
                repo + "\n"
            )

    # --------------------------------------------------------
    # Final output
    # --------------------------------------------------------

    print("=" * 70)
    print("COLLECTION COMPLETE")
    print("=" * 70)

    print(
        f"New repositories added: "
        f"{len(collected)}"
    )

    print(
        f"Output file: "
        f"{OUTPUT_FILE}"
    )

    print(
        f"Total repositories now: "
        f"{len(existing) + len(collected)}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()