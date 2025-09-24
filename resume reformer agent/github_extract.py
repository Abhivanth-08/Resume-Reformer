import requests

def fetch_projects_from_subfolders(repo_owner, repo_name):
    base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents"
    headers = {"Accept": "application/vnd.github.v3+json"}
    response = requests.get(base_url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to access repo: {response.status_code}")
        return []
    contents = response.json()
    projects = []
    for item in contents:
        if item["type"] == "dir":
            subfolder = item["name"]
            readme_url = f"{base_url}/{subfolder}/README.md"
            readme_resp = requests.get(readme_url, headers=headers)

            if readme_resp.status_code == 200:
                readme_data = readme_resp.json()
                readme_content = requests.get(readme_data["download_url"]).text
                summary = readme_content.strip().split("\n")[0]  # Take first line
                projects.append(f"{subfolder}: {summary}")
            else:
                projects.append(f"{subfolder}")
    return projects


