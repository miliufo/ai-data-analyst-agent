import os
import json

from openai import OpenAI
from dotenv import load_dotenv

from app.data.schema_inspector import get_database_schema
from app.tools.sql_validator import validate_sql
from app.tools.database_tools import execute_query


load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)


def generate_sql(question: str) -> dict:
    """
    Convert a natural-language analytics question
    into a safe SQL query.
    """

    schema = get_database_schema()

    prompt = f"""
You are a senior data analyst specialized in DuckDB SQL.

DATABASE SCHEMA:
{schema}

USER QUESTION:
{question}

Rules:
- Generate SQL only for the table named sales.
- Use only columns that exist in the schema.
- Produce a read-only query.
- Never generate INSERT, UPDATE, DELETE, DROP, ALTER,
  CREATE, TRUNCATE, COPY, ATTACH, INSTALL, or LOAD.
- Prefer simple and efficient SQL.
- If the question asks for ranking, sort appropriately.
- If the question asks for "highest", "top", "most",
  normally use ORDER BY ... DESC and LIMIT when appropriate.
- For date analysis, use DuckDB-compatible SQL.
- Do not answer the question yourself.

Return ONLY valid JSON in this exact structure:

{{
  "sql": "SELECT ...",
  "explanation": "Short description of what the query does"
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

    raw_output = response.choices[0].message.content

    return json.loads(raw_output)


def run_sql_agent(question: str) -> dict:
    """
    Generate SQL, validate it, and execute it.
    """

    generated = generate_sql(question)

    sql = generated.get(
        "sql",
        ""
    )

    validation = validate_sql(sql)

    if not validation["valid"]:

        return {
            "success": False,
            "question": question,
            "sql": sql,
            "validation": validation,
            "error": (
                "The generated SQL query was blocked "
                "by the SQL safety validator."
            )
        }

    query_result = execute_query(sql)

    if not query_result["success"]:

        return {
            "success": False,
            "question": question,
            "sql": sql,
            "validation": validation,
            "error": query_result["error"]
        }

    return {
        "success": True,
        "question": question,
        "sql": sql,
        "sql_explanation": generated.get(
            "explanation",
            ""
        ),
        "validation": validation,
        "columns": query_result["columns"],
        "rows": query_result["rows"]
    }