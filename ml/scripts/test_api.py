from github_api import get_github_data

repo = "https://github.com/pallets/flask"

data = get_github_data(repo)

print(data)