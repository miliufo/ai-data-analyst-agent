from app.graph.analyst_graph import analyst_graph


def run_question(question: str):

    initial_state = {
        "question": question,
        "plan": {},
        "sql_result": {},
        "analysis": "",
        "visualization": {},
        "final_response": ""
    }

    result = analyst_graph.invoke(initial_state)

    print()
    print("📊 AI DATA ANALYST")
    print("==================")
    print()

    print("QUESTION:")
    print(question)

    print()
    print("PLAN:")
    print(result["plan"])

    print()
    print("SQL:")
    print(result["sql_result"].get("sql"))

    print()
    print("RESULT:")
    print(result["sql_result"].get("rows"))

    print()
    print("ANALYSIS:")
    print(result["analysis"])

    print()
    print("VISUALIZATION:")
    print(result["visualization"])


def main():

    run_question(
        "Show total revenue for each region from highest to lowest."
    )


if __name__ == "__main__":
    main()