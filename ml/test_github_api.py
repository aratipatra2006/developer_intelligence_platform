import requests

repo = "pallets/flask"

url = f"https://api.github.com/repos/{repo}"

response = requests.get(url)

print("Status Code:", response.status_code)

if response.status_code == 200:
    data = response.json()

    print("Repository:", data["full_name"])
    print("Stars:", data["stargazers_count"])
    print("Forks:", data["forks_count"])
    print("Watchers:", data["watchers_count"])
    print("Open Issues:", data["open_issues_count"])
    print("Language:", data["language"])
    print("Size:", data["size"])
else:
    print(response.text)