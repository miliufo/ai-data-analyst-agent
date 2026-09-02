import pandas as pd
import plotly.express as px


def create_chart(
    rows: list,
    chart_type: str,
    x: str,
    y: str,
    title: str
):
    """
    Create a Plotly chart from query results.
    """

    if not rows:
        return None

    df = pd.DataFrame(rows)

    if chart_type == "bar":
        return px.bar(
            df,
            x=x,
            y=y,
            title=title
        )

    if chart_type == "line":
        return px.line(
            df,
            x=x,
            y=y,
            title=title,
            markers=True
        )

    if chart_type == "pie":
        return px.pie(
            df,
            names=x,
            values=y,
            title=title
        )

    return None