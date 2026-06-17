import os
import requests
from dotenv import load_dotenv
from ai_reviewer_graph import build_ai_reviewer_graph

load_dotenv()


def get_required_env(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise ValueError(f"{name} is missing")

    return value


def github_headers() -> dict:
    github_token = get_required_env("GITHUB_TOKEN")

    return {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def fetch_pr_details() -> dict:
    repo = get_required_env("GITHUB_REPOSITORY")
    pr_number = get_required_env("PR_NUMBER")

    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"

    response = requests.get(url, headers=github_headers(), timeout=30)

    print(f"Fetch PR details status code: {response.status_code}", flush=True)

    if response.status_code != 200:
        print(response.text, flush=True)
        response.raise_for_status()

    return response.json()


def fetch_pr_files() -> list:
    repo = get_required_env("GITHUB_REPOSITORY")
    pr_number = get_required_env("PR_NUMBER")

    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"

    response = requests.get(url, headers=github_headers(), timeout=30)

    print(f"Fetch PR files status code: {response.status_code}", flush=True)

    if response.status_code != 200:
        print(response.text, flush=True)
        response.raise_for_status()

    return response.json()


def post_inline_comment(commit_id: str, path: str, line: int, body: str) -> None:
    repo = get_required_env("GITHUB_REPOSITORY")
    pr_number = get_required_env("PR_NUMBER")

    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/comments"

    payload = {
        "body": body,
        "commit_id": commit_id,
        "path": path,
        "line": line,
        "side": "RIGHT",
    }

    response = requests.post(url, headers=github_headers(), json=payload, timeout=30)

    print(
        f"Post inline comment status code for {path}:{line}: {response.status_code}",
        flush=True,
    )

    if response.status_code not in [200, 201]:
        print(response.text, flush=True)
        response.raise_for_status()


def main():
    print("AI reviewer is running", flush=True)

    pr_details = fetch_pr_details()
    commit_id = pr_details["head"]["sha"]

    print(f"PR head commit SHA: {commit_id}", flush=True)

    changed_files = fetch_pr_files()

    print(f"Changed files count: {len(changed_files)}", flush=True)

    graph = build_ai_reviewer_graph()

    result = graph.invoke(
        {
            "changed_files": changed_files,
            "added_lines": [],
            "inline_comments": [],
        }
    )

    inline_comments = result["inline_comments"]

    print("=" * 80, flush=True)
    print("AI INLINE COMMENTS OUTPUT", flush=True)
    print("=" * 80, flush=True)

    if not inline_comments:
        print("No inline comments suggested by AI.", flush=True)
        return

    for comment in inline_comments:
        path = comment["path"]
        line = int(comment["line"])
        body = comment["body"]

        print(f"File: {path}", flush=True)
        print(f"Line: {line}", flush=True)
        print(f"Comment: {body}", flush=True)
        print("-" * 80, flush=True)

        post_inline_comment(
            commit_id=commit_id,
            path=path,
            line=line,
            body=body,
        )

    print("Finished posting inline comments.", flush=True)


if __name__ == "__main__":
    main()