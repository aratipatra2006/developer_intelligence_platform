import re


def validate_github_url(url):
    """
    Validates whether the given URL is a public GitHub repository URL.
    """

    pattern = r"^https://github\.com/[\w.-]+/[\w.-]+/?$"

    return re.match(pattern, url) is not None