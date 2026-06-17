import json
import re
from typing import TypedDict, List, Dict

from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
import os
from dotenv import  load_dotenv
load_dotenv()


class InlineComment(BaseModel):
    path: str = Field(description="File path where the inline comment should be placed")
    line: int = Field(description="Line number in the new version of the file")
    body: str = Field(description="Inline review comment body")


class InlineReviewResult(BaseModel):
    comments: List[InlineComment] = Field(
        description="List of suggested inline PR comments"
    )


class PRReviewState(TypedDict):
    changed_files: List[Dict]
    added_lines: List[Dict]
    inline_comments: List[Dict]


model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)

structured_model = model.with_structured_output(InlineReviewResult)


def extract_added_lines_from_patch(filename: str, patch: str) -> List[Dict]:
    """
    Extract only added lines from a GitHub PR patch.

    GitHub patch example:
    @@ -1,4 +1,6 @@
     existing line
    +new line

    We track the new file line number and only keep lines starting with '+',
    excluding patch metadata like '+++'.
    """

    added_lines = []
    new_line_number = None

    for patch_line in patch.splitlines():
        hunk_match = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", patch_line)

        if hunk_match:
            new_line_number = int(hunk_match.group(1))
            continue

        if new_line_number is None:
            continue

        if patch_line.startswith("+") and not patch_line.startswith("+++"):
            code_line = patch_line[1:]

            added_lines.append({
                "path": filename,
                "line": new_line_number,
                "code": code_line
            })

            new_line_number += 1

        elif patch_line.startswith("-") and not patch_line.startswith("---"):
            # Deleted line exists only in old file, so it does not advance new file line number
            continue

        else:
            # Context line exists in new file, so it advances new file line number
            new_line_number += 1

    return added_lines


def prepare_added_lines_node(state: PRReviewState) -> PRReviewState:
    changed_files = state["changed_files"]

    all_added_lines = []

    for changed_file in changed_files:
        filename = changed_file.get("filename", "unknown")
        patch = changed_file.get("patch", "")

        if not patch:
            continue

        file_added_lines = extract_added_lines_from_patch(filename, patch)
        all_added_lines.extend(file_added_lines)

    print(f"prepare_added_lines_node completed. Added lines found: {len(all_added_lines)}", flush=True)

    return {
        "added_lines": all_added_lines
    }


def ai_inline_review_node(state: PRReviewState) -> PRReviewState:
    added_lines = state["added_lines"]

    if not added_lines:
        print("No added lines found for inline review.", flush=True)
        return {
            "inline_comments": []
        }

    allowed_lines_json = json.dumps(added_lines, indent=2)

    prompt = f"""
You are an AI GitHub Pull Request reviewer.

You must suggest inline comments only for the added lines provided below.

Rules:
- Return at most 3 inline comments.
- Only comment if there is a useful issue, risk, bug, missing validation, poor naming, or maintainability concern.
- Do not comment on every line.
- Do not invent file paths.
- Do not invent line numbers.
- The path and line must exactly match one of the provided added lines.
- Keep each comment concise and helpful.
- If there are no useful comments, return an empty comments list.

Allowed added lines:

{allowed_lines_json}
"""

    response = structured_model.invoke(prompt)

    inline_comments = [
        {
            "path": comment.path,
            "line": comment.line,
            "body": comment.body
        }
        for comment in response.comments
    ]

    print(f"ai_inline_review_node completed. Inline comments suggested: {len(inline_comments)}", flush=True)

    return {
        "inline_comments": inline_comments
    }


def build_ai_reviewer_graph():
    graph = StateGraph(PRReviewState)

    graph.add_node("prepare_added_lines", prepare_added_lines_node)
    graph.add_node("ai_inline_review", ai_inline_review_node)

    graph.add_edge(START, "prepare_added_lines")
    graph.add_edge("prepare_added_lines", "ai_inline_review")
    graph.add_edge("ai_inline_review", END)

    return graph.compile()