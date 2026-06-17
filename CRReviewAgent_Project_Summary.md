# CRReviewAgent – AI Pull Request Code Review Agent

## 1. High-Level Overview

CRReviewAgent is an AI-assisted Pull Request review system added to an existing **Spring Boot repository**. The main application remains a Java/Spring Boot project, but a new Python-based code review agent is added inside the repository to automate PR review.

The agent runs when a GitHub Pull Request is opened, updated, or reopened. It uses **GitHub Actions** as the trigger, the **GitHub API** to fetch changed files and diffs, **LangGraph** to organize the review workflow, and **OpenAI** to generate AI-powered code review feedback. The feedback can then be posted directly as inline comments on the Pull Request.

High-level flow:

```text
Developer opens or updates a PR
        ↓
GitHub Actions starts the workflow
        ↓
Python reviewer script runs
        ↓
GitHub API fetches PR details and changed files
        ↓
LangGraph processes the PR diff
        ↓
OpenAI generates review comments
        ↓
CRReviewAgent posts inline comments into the PR
```

The project demonstrates how an AI agent can be integrated directly into a real software engineering workflow instead of being used only as a chatbot.

---

## 2. Project Goal

The goal of this project is to build an MVP AI Code Review Agent that can:

1. Detect Pull Request events.
2. Read changed files from a PR.
3. Extract useful diff information from GitHub patches.
4. Pass the PR data through a LangGraph workflow.
5. Use OpenAI to generate review comments.
6. Post review feedback directly into the Pull Request.
7. Clearly identify the feedback as coming from **CRReviewAgent**.

This MVP focuses on proving the complete automation pipeline first. More advanced agent behavior can be added later.

---

## 3. Repository Context

The target repository is a Spring Boot application:

```text
SaiGit-source/SpringWebApp
```

The AI reviewer is added as a separate automation folder inside the same repository:

```text
AICodeReviewer_MVP/
```

The Spring Boot app remains the main project. The Python AI reviewer acts as a DevOps/AI automation layer that reviews code changes made to the Spring Boot repository.

Example project structure:

```text
SpringWebApp/
├── src/
│   └── main/
│       └── java/
│           └── ... Spring Boot application code ...
├── AICodeReviewer_MVP/
│   ├── ai_reviewer.py
│   ├── ai_reviewer_graph.py
│   ├── github_api_test.py
│   └── langgraph_test.py
├── .github/
│   └── workflows/
│       ├── test-action.yml
│       ├── test-github-api.yml
│       ├── test-langgraph.yml
│       └── ai-code-reviewer.yml
├── requirements.txt
└── .env
```

The `.env` file is used only for local development and must not be committed.

---

## 4. Technologies Used

### Spring Boot

The reviewed repository is a Java/Spring Boot project. This makes the project realistic because the agent is designed to review backend application code such as controllers, services, configuration files, and Java changes.

### Python

Python is used to implement the AI reviewer because it is lightweight, easy to run in GitHub Actions, and has strong AI tooling support.

### GitHub Actions

GitHub Actions triggers the reviewer workflow whenever a PR is opened, synchronized, or reopened.

```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened]
```

### GitHub API

The GitHub API is used to fetch PR details, fetch changed files, and post inline comments.

Important API actions include:

```text
GET /repos/{owner}/{repo}/pulls/{pull_number}
GET /repos/{owner}/{repo}/pulls/{pull_number}/files
POST /repos/{owner}/{repo}/pulls/{pull_number}/comments
```

### LangGraph

LangGraph organizes the reviewer as a workflow graph. Instead of writing one large script, the logic is split into clear nodes.

Current graph flow:

```text
prepare_added_lines_node
        ↓
ai_inline_review_node
```

### OpenAI

OpenAI is used through `langchain-openai` to generate the actual code review comments.

Example model setup:

```python
ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)
```

### Pydantic

Pydantic is used to force structured AI output. This is useful because inline comments need specific fields:

```text
path
line
body
```

---

## 5. Development Stages

### Stage 1: Test GitHub Actions

The first step was to verify that GitHub Actions could detect a Pull Request event.

Workflow file:

```text
.github/workflows/test-action.yml
```

This workflow printed basic values such as repository name, PR number, and branch name.

This proved:

```text
Pull Request event → GitHub Actions workflow
```

---

### Stage 2: Test GitHub API Locally

A local Python script was created:

```text
AICodeReviewer_MVP/github_api_test.py
```

This script connected to GitHub, fetched PR changed files, and printed file details.

Example successful output:

```text
GitHub API test is running
Repository: SaiGit-source/SpringWebApp
Pull Request Number: 1
GitHub API status code: 200
Changed files count: 1
Filename: .github/workflows/test-action.yml
Status: added
Additions: 17
Deletions: 0
Patch:
...
```

This proved:

```text
Local Python script → GitHub API → PR changed files
```

---

### Stage 3: Test GitHub API in GitHub Actions

The next step was to move the GitHub API test into GitHub Actions.

Workflow file:

```text
.github/workflows/test-github-api.yml
```

This proved:

```text
Pull Request event
        ↓
GitHub Actions
        ↓
Python script
        ↓
GitHub API
        ↓
Changed PR files
```

---

### Stage 4: Test LangGraph Separately

A separate LangGraph test file was created:

```text
AICodeReviewer_MVP/langgraph_test.py
```

This used sample changed-file data and passed it through a simple LangGraph node.

This proved:

```text
Sample PR data → LangGraph node → review output
```

---

### Stage 5: Connect GitHub API to LangGraph

The main runner file was created:

```text
AICodeReviewer_MVP/ai_reviewer.py
```

This file fetches PR data and invokes the LangGraph workflow.

This proved:

```text
GitHub Actions
        ↓
GitHub API
        ↓
Changed PR files
        ↓
LangGraph
        ↓
Review output
```

---

### Stage 6: Add OpenAI Review Logic

OpenAI was then added in a separate LangGraph node.

The graph was intentionally split into separate responsibilities:

```text
prepare_added_lines_node
        ↓
ai_inline_review_node
```

This makes the system easier to debug and easier to extend later.

---

### Stage 7: Generate Inline Comments

The agent was improved to generate inline comments instead of only one large summary.

The system extracts added lines from the PR patch and sends only valid added lines to the AI. The AI is instructed not to invent file paths or line numbers.

Expected AI output structure:

```json
{
  "comments": [
    {
      "path": "AICodeReviewer_MVP/ai_reviewer.py",
      "line": 12,
      "body": "Consider validating this value before using it."
    }
  ]
}
```

---

### Stage 8: Post Inline Comments to the Pull Request

The runner posts inline comments back to the Pull Request using the GitHub API.

Required inline comment fields:

```text
commit_id
path
line
side
body
```

Example payload:

```json
{
  "body": "**CRReviewAgent**\n\nConsider validating this value before using it.",
  "commit_id": "latest PR head SHA",
  "path": "AICodeReviewer_MVP/ai_reviewer.py",
  "line": 12,
  "side": "RIGHT"
}
```

The comments are posted by `github-actions[bot]`, but the body starts with **CRReviewAgent** so the reviewer identity is clear.

---

## 6. Main Files

### `AICodeReviewer_MVP/ai_reviewer.py`

This is the main runner file. It:

1. Loads environment variables.
2. Fetches PR details.
3. Gets the latest PR head commit SHA.
4. Fetches changed PR files.
5. Invokes the LangGraph workflow.
6. Reads AI-generated inline comments.
7. Posts inline comments back to the PR.

Main functions:

```python
fetch_pr_details()
fetch_pr_files()
post_inline_comment()
main()
```

---

### `AICodeReviewer_MVP/ai_reviewer_graph.py`

This file defines the LangGraph workflow.

It contains:

```python
InlineComment
InlineReviewResult
PRReviewState
extract_added_lines_from_patch()
prepare_added_lines_node()
ai_inline_review_node()
build_ai_reviewer_graph()
```

Current graph:

```text
START
  ↓
prepare_added_lines
  ↓
ai_inline_review
  ↓
END
```

---

### `AICodeReviewer_MVP/github_api_test.py`

This was used to test whether Python could fetch PR changed files from GitHub.

---

### `AICodeReviewer_MVP/langgraph_test.py`

This was used to test LangGraph separately before connecting it to GitHub API data.

---

### `.github/workflows/ai-code-reviewer.yml`

This is the real GitHub Actions workflow for CRReviewAgent.

It runs:

```text
AICodeReviewer_MVP/ai_reviewer.py
```

It needs permissions such as:

```yaml
permissions:
  contents: read
  pull-requests: write
```

---

### `requirements.txt`

Current dependencies:

```text
requests
python-dotenv
langgraph
langchain-openai
pydantic
```

---

## 7. Environment Variables and Secrets

### Local `.env`

For local testing:

```env
OPENAI_API_KEY=your_openai_key
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_REPOSITORY=SaiGit-source/SpringWebApp
PR_NUMBER=1
```

`.env` must be in `.gitignore`.

### GitHub Actions Secrets

In GitHub Actions, `OPENAI_API_KEY` is stored as a repository secret.

The workflow passes it into Python:

```yaml
OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

GitHub automatically provides other values:

```yaml
GITHUB_TOKEN: ${{ github.token }}
GITHUB_REPOSITORY: ${{ github.repository }}
PR_NUMBER: ${{ github.event.pull_request.number }}
```

---

## 8. How Inline Comment Extraction Works

GitHub returns patch data in diff format:

```diff
@@ -1,4 +1,6 @@
 existing line
+new line
```

The agent parses the patch and tracks new file line numbers.

It keeps only added lines:

```json
{
  "path": "AICodeReviewer_MVP/ai_reviewer.py",
  "line": 12,
  "code": "new code line"
}
```

These allowed lines are passed to OpenAI. The prompt tells the AI:

1. Only comment on provided added lines.
2. Do not invent paths.
3. Do not invent line numbers.
4. Return at most 3 comments.
5. Return an empty list if there are no useful comments.

This makes inline comments safer because GitHub requires valid diff line locations.

---

## 9. Why LangGraph Is Useful Here

LangGraph makes the reviewer modular.

Current MVP:

```text
prepare_added_lines_node
        ↓
ai_inline_review_node
```

Possible future graph:

```text
prepare_diff_node
        ↓
classify_risk_node
        ↓
security_review_node / spring_boot_review_node / test_review_node
        ↓
post_comment_node
```

This makes it easier to expand the project into a multi-step or multi-agent reviewer.

---

## 10. Current MVP Capabilities

The current MVP can:

1. Run automatically on Pull Request events.
2. Fetch PR details and changed files.
3. Extract added lines from patches.
4. Use LangGraph to process the review workflow.
5. Use OpenAI to generate structured inline comments.
6. Post inline comments directly into GitHub Pull Requests.
7. Prefix comments with **CRReviewAgent**.

---

## 11. Current Limitations

The MVP currently has these limitations:

1. It focuses mainly on added lines.
2. It does not yet avoid duplicate comments across repeated runs.
3. It does not yet group comments into one GitHub review.
4. It does not yet create a full PR summary comment.
5. It does not yet use multiple specialized agents.
6. It does not yet analyze the full Spring Boot project context.
7. It may fail on forked PRs because GitHub restricts secrets and write permissions.
8. The visible GitHub author is still `github-actions[bot]`, although comments are labeled as `CRReviewAgent`.

---

## 12. Future Improvements

Possible next improvements:

1. Add a full PR summary comment.
2. Prevent duplicate CRReviewAgent comments.
3. Group inline comments into one GitHub review.
4. Add risk classification.
5. Add specialized review nodes:
   - Security reviewer
   - Spring Boot best-practices reviewer
   - Test coverage reviewer
   - Performance reviewer
6. Add Java/Spring static analysis.
7. Add full-file context review.
8. Create a GitHub App named `CRReviewAgent`.
9. Store review history as artifacts or in a database.
10. Add configuration for ignored paths and maximum comments.

---

## 13. Portfolio Explanation

Built **CRReviewAgent**, an AI-powered Pull Request review agent integrated into a Spring Boot repository. The system uses GitHub Actions to trigger on PR events, GitHub API to fetch changed files and patches, LangGraph to orchestrate the review workflow, and OpenAI to generate structured inline code review comments. The agent posts review feedback directly into GitHub Pull Requests, demonstrating practical AI agent integration into a real software engineering workflow.

---

## 14. Resume Bullet Version

- Built an AI-powered Pull Request review agent for a Spring Boot repository using Python, LangGraph, GitHub Actions, GitHub API, and OpenAI.
- Automated PR review workflows by fetching changed files, extracting diff patches, generating AI-based inline feedback, and posting comments directly to GitHub Pull Requests.
- Designed a LangGraph-based workflow with separate nodes for patch processing and AI inline review generation.
- Implemented secure secret handling using GitHub Actions secrets and local `.env` configuration for development.
- Integrated structured AI output using Pydantic to produce reliable file-path, line-number, and comment-body mappings for GitHub inline comments.

---

## 15. Interview Explanation

In this project, I took an existing Spring Boot repository and added an AI-powered code review automation layer called CRReviewAgent. The Spring Boot application remains the main project, but I added a Python-based agent inside the repository to review code changes automatically.

When a developer opens or updates a Pull Request, GitHub Actions triggers the reviewer workflow. The Python script uses the GitHub API to fetch the PR details and changed files. It then extracts the added lines from the diff and passes them into a LangGraph workflow.

The LangGraph workflow currently has two main nodes. The first node prepares the added lines from the patch data. The second node calls OpenAI and asks it to generate useful inline review comments only for valid added lines. The output is structured using Pydantic, so each comment contains the file path, line number, and comment body.

Finally, the script posts those comments back into the Pull Request using GitHub’s PR review comment API. The comments are marked with `CRReviewAgent` in the body, so reviewers can clearly identify them as AI-generated suggestions.

This project demonstrates how AI agents can be integrated directly into the software development lifecycle, especially in Pull Request review workflows.
