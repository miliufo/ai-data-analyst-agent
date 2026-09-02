from app.tools.database_tools import create_connection


def get_database_schema() -> str:
    """
    Return the schema of the sales table
    in a format suitable for an AI agent.
    """

    connection = create_connection()

    try:
        result = connection.execute(
            "DESCRIBE sales"
        ).fetchall()

        schema_lines = []

        for row in result:
            column_name = row[0]
            column_type = row[1]

            schema_lines.append(
                f"- {column_name}: {column_type}"
            )

        return (
            "Table: sales\n\n"
            "Columns:\n"
            + "\n".join(schema_lines)
        )

    finally:
        connection.close()