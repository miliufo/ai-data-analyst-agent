from langgraph.graph import StateGraph, START, END

from app.graph.state import AnalystState

from app.agents.planner_agent import plan_analysis
from app.agents.visualization_agent import run_visualization_agent


def planner_node(state: AnalystState):
    plan = plan_analysis(
        state["question"]
    )

    return {
        "plan": plan
    }


def analytics_node(state: AnalystState):
    result = run_visualization_agent(
        state["question"]
    )

    if not result["success"]:
        return {
            "sql_result": result,
            "analysis": "",
            "visualization": {},
            "final_response": (
                result.get("error")
                or "The analysis could not be completed."
            )
        }

    return {
        "sql_result": {
            "sql": result["sql"],
            "validation": result["validation"],
            "columns": result["columns"],
            "rows": result["rows"]
        },
        "analysis": result["analysis"],
        "visualization": result["visualization"],
        "final_response": result["analysis"]
    }


builder = StateGraph(AnalystState)

builder.add_node(
    "planner",
    planner_node
)

builder.add_node(
    "analytics",
    analytics_node
)

builder.add_edge(
    START,
    "planner"
)

builder.add_edge(
    "planner",
    "analytics"
)

builder.add_edge(
    "analytics",
    END
)

analyst_graph = builder.compile()