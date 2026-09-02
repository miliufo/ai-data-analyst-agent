from typing import TypedDict, Any


class AnalystState(TypedDict):
    question: str

    plan: dict[str, Any]

    sql_result: dict[str, Any]

    analysis: str

    visualization: dict[str, Any]

    final_response: str