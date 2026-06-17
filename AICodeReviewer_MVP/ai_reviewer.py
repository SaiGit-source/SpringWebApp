import os
import requests
from dotenv import load_dotenv
from ai_reviewer_graph import build_ai_reviewer_graph

load_dotenv()


def fetch_pr_files():
    github_token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY")
    pr_number = os.getenv("PR_NUMBER")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    print("OPENAI_API_KEY exists:", bool(os.getenv("OPENAI_API_KEY")), flush=True) 

    if not github_token:
        raise ValueError("GITHUB_TOKEN is missing")

    if not repo:
        raise ValueError("GITHUB_REPOSITORY is missing")

    if not pr_number:
        raise ValueError("PR_NUMBER is missing")
    
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY is missing")

    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"

    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
    }

    response = requests.get(url, headers=headers, timeout=30)

    print(f"GitHub API status code: {response.status_code}", flush=True)

    if response.status_code != 200:
        print(response.text, flush=True)
        response.raise_for_status()

    return response.json()


def main():
    print("AI reviewer is running", flush=True)

    changed_files = fetch_pr_files()

    print(f"Changed files count: {len(changed_files)}", flush=True)

    graph = build_ai_reviewer_graph()

    result = graph.invoke({
        "changed_files": changed_files,
        "added_lines": [],
        "inline_comments": []
    })

    print("=" * 80, flush=True)
    print("AI INLINE COMMENTS OUTPUT", flush=True)
    print("=" * 80, flush=True)

    for comment in result["inline_comments"]:
        print(f"File: {comment['path']}", flush=True)
        print(f"Line: {comment['line']}", flush=True)
        print(f"Comment: {comment['body']}", flush=True)
        print("-" * 80, flush=True)

if __name__ == "__main__":
    main()