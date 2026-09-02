import os
import json

from openai import OpenAI
from dotenv import load_dotenv

from app.agents.analysis_agent import run_analysis_agent


load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)


def choose_visualization(
    question: str,
    columns: list,
    rows: list
) -> dict:
    """
    Decide whether the SQL result should be visualized
    and select an appropriate chart configuration.
    """

    prompt = f"""
You are a data visualization expert.

USER QUESTION:
{question}

AVAILABLE COLUMNS:
{json.dumps(columns)}

DATA:
{json.dumps(rows, indent=2, default=str)}

Decide whether a chart would help the user understand the result.

Allowed chart types:
- bar
- line
- pie
- none

Guidelines:
- Use bar for comparing categories, products, customers, or regions.
- Use line for trends over time.
- Use pie only for simple part-to-whole comparisons with few categories.
- Use none when there is only one value or a chart adds little value.
- x must be an existing column.
- y must be an existing numeric column.
- Do not invent column names.

Return ONLY JSON:

{{
    "chart_type": "bar",
    "x": "region",
    "y": "total_revenue",
    "title": "Revenue by Region",
    "reason": "A bar chart clearly compares revenue across regions."
}}
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format={
            "type": "json_object"
        }
    )

    return json.loads(
        response.choices[0].message.content
    )


def run_visualization_agent(question: str) -> dict:
    """
    Run analytics pipeline and determine
    the best visualization.
    """

    analysis_result = run_analysis_agent(question)

    if not analysis_result["success"]:
        return analysis_result

    visualization = choose_visualization(
        question=question,
        columns=analysis_result["columns"],
        rows=analysis_result["rows"]
    )

    return {
        **analysis_result,
        "visualization": visualization
    }