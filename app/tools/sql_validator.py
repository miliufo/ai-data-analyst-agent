import re


BLOCKED_KEYWORDS = [
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "CREATE",
    "TRUNCATE",
    "REPLACE",
    "MERGE",
    "COPY",
    "ATTACH",
    "DETACH",
    "INSTALL",
    "LOAD"
]


def validate_sql(sql: str) -> dict:
    """
    Validate that an AI-generated SQL query is read-only.
    """

    cleaned_sql = sql.strip()

    if not cleaned_sql:
        return {
            "valid": False,
            "reason": "SQL query is empty."
        }

    # Only SELECT or WITH queries are allowed
    if not re.match(
        r"^(SELECT|WITH)\b",
        cleaned_sql,
        re.IGNORECASE
    ):
        return {
            "valid": False,
            "reason": "Only read-only SELECT queries are allowed."
        }

    upper_sql = cleaned_sql.upper()

    for keyword in BLOCKED_KEYWORDS:

        if re.search(
            rf"\b{keyword}\b",
            upper_sql
        ):
            return {
                "valid": False,
                "reason": f"Blocked SQL keyword detected: {keyword}"
            }

    # Prevent multiple SQL statements
    statements = [
        statement.strip()
        for statement in cleaned_sql.split(";")
        if statement.strip()
    ]

    if len(statements) > 1:
        return {
            "valid": False,
            "reason": "Multiple SQL statements are not allowed."
        }

    return {
        "valid": True,
        "reason": "Query passed SQL safety validation."
    }