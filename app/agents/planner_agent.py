import os
import json

from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)


def plan_analysis(question: str) -> dict:
    """
    Decide the analytical intent of the user's question.
    """

    prompt = f"""
You are a senior analytics planning agent.

USER QUESTION:
{question}

Determine the analytical intent.

Return ONLY JSON:

{{
  "intent": "ranking",
  "needs_sql": true,
  "needs_visualization": true,
  "reason": "Short reason"
}}

Allowed intent values:
- ranking
- comparison
- trend
- aggregation
- lookup
- summary
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