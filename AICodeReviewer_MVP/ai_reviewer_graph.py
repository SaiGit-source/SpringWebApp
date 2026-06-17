from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, START, END


class PRReviewState(TypedDict):
    changed_files: List[Dict]
    review_comment: str


def review_pr_node(state: PRReviewState) -> PRReviewState:
    changed_files = state["changed_files"]

    lines = []
    lines.append("## AI Code Review - Initial LangGraph Test")
    lines.append("")
    lines.append(f"Files reviewed: {len(changed_files)}")
    lines.append("")

    for file in changed_files:
        filename = file.get("filename", "unknown")
        status = file.get("status", "unknown")
        additions = file.get("additions", 0)
        deletions = file.get("deletions", 0)
        patch = file.get("patch", "")

        lines.append(f"### {filename}")
        lines.append(f"- Status: {status}")
        lines.append(f"- Additions: {additions}")
        lines.append(f"- Deletions: {deletions}")
        lines.append("")
        lines.append("Changed code preview:")
        lines.append("```diff")
        lines.append(patch[:1000])
        lines.append("```")
        lines.append("")

    lines.append("✅ LangGraph successfully received the PR diff data.")

    return {
        "review_comment": "\n".join(lines)
    }


def build_ai_reviewer_graph():
    graph = StateGraph(PRReviewState)

    graph.add_node("review_pr", review_pr_node)

    graph.add_edge(START, "review_pr")
    graph.add_edge("review_pr", END)

    return graph.compile()