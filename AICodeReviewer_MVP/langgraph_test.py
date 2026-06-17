from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, END


class ReviewState(TypedDict):
    changed_files: List[Dict]
    review_summary: str


def analyze_pr_node(state: ReviewState) -> ReviewState:
    changed_files = state["changed_files"]

    lines = []
    lines.append("LangGraph test is running")
    lines.append("")
    lines.append(f"Number of changed files: {len(changed_files)}")
    lines.append("")

    for file in changed_files:
        lines.append(f"File: {file['filename']}")
        lines.append(f"Status: {file['status']}")
        lines.append(f"Additions: {file['additions']}")
        lines.append(f"Deletions: {file['deletions']}")
        lines.append("")

    lines.append("Result: PR data successfully passed through LangGraph.")

    state["review_summary"] = "\n".join(lines)
    return state


def build_graph():
    graph = StateGraph(ReviewState)

    graph.add_node("analyze_pr", analyze_pr_node)

    graph.set_entry_point("analyze_pr")
    graph.add_edge("analyze_pr", END)

    return graph.compile()


if __name__ == "__main__":
    sample_changed_files = [
        {
            "filename": ".github/workflows/test-action.yml",
            "status": "added",
            "additions": 17,
            "deletions": 0,
        },
        {
            "filename": "src/main/java/com/example/DemoController.java",
            "status": "modified",
            "additions": 8,
            "deletions": 2,
        },
    ]

    app = build_graph()

    result = app.invoke(
        {
            "changed_files": sample_changed_files,
            "review_summary": "",
        }
    )

    print("=" * 80)
    print("LANGGRAPH TEST OUTPUT")
    print("=" * 80)
    print(result["review_summary"])