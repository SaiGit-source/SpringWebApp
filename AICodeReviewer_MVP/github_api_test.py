import os
import requests
from dotenv import load_dotenv

load_dotenv()

def main():
    github_token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY")
    pr_number = os.getenv("PR_NUMBER")

    if not github_token:
        raise ValueError("GITHUB_TOKEN is missing")

    if not repo:
        raise ValueError("GITHUB_REPOSITORY is missing")

    if not pr_number:
        raise ValueError("PR_NUMBER is missing")

    print("GitHub API test is running")
    print(f"Repository: {repo}")
    print(f"Pull Request Number: {pr_number}")

    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"

    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
    }

    response = requests.get(url, headers=headers, timeout=30)

    print(f"GitHub API status code: {response.status_code}")

    if response.status_code != 200:
        print(response.text)
        response.raise_for_status()

    files = response.json()

    print(f"Changed files count: {len(files)}")

    for file in files:
        print("=" * 80)
        print(f"Filename: {file.get('filename')}")
        print(f"Status: {file.get('status')}")
        print(f"Additions: {file.get('additions')}")
        print(f"Deletions: {file.get('deletions')}")
        print("Patch:")
        print(file.get("patch", "No patch available"))


if __name__ == "__main__":
    main()