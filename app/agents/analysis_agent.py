import os
import json

from openai import OpenAI
from dotenv import load_dotenv

from app.agents.sql_agent import run_sql_agent


load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)


def generate_analysis(
    question: str,
    sql: str,
    rows: list
) -> str:
    """
    Convert SQL results into a concise,
    user-friendly business insight.
    """

    prompt = f"""
You are a senior business data analyst.

USER QUESTION:
{question}

SQL QUERY:
{sql}

QUERY RESULT:
{json.dumps(rows, indent=2, default=str)}

Your task:
- Answer the user's question directly.
- Base your answer ONLY on the provided query result.
- Never invent numbers or facts.
- Highlight important numbers.
- Keep the answer concise and professional.
- Mention comparisons or trends only when supported by the data.
- Do not discuss SQL unless necessary.
- Format currency values clearly when relevant.

Return only the final analysis.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content.strip()


def run_analysis_agent(question: str) -> dict:
    """
    Run the SQL agent and generate
    a natural-language analysis.
    """

    sql_result = run_sql_agent(question)

    if not sql_result["success"]:
        return sql_result

    analysis = generate_analysis(
        question=question,
        sql=sql_result["sql"],
        rows=sql_result["rows"]
    )

    return {
        **sql_result,
        "analysis": analysis
    }