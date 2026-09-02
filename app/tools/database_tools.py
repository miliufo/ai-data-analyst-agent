import duckdb

from app.data.loader import (
    load_dataset,
    DEFAULT_CSV_PATH,
)


CURRENT_DATASET_PATH = DEFAULT_CSV_PATH


def set_dataset_path(
    csv_path: str
):
    """
    Change the active CSV dataset used by the agent.
    """

    global CURRENT_DATASET_PATH

    CURRENT_DATASET_PATH = csv_path


def get_dataset_path() -> str:
    """
    Return the currently active dataset path.
    """

    return CURRENT_DATASET_PATH


def create_connection():
    """
    Create an in-memory DuckDB connection
    and register the active CSV as the 'sales' table.
    """

    connection = duckdb.connect(
        database=":memory:"
    )

    dataframe = load_dataset(
        CURRENT_DATASET_PATH
    )

    connection.register(
        "sales",
        dataframe
    )

    return connection


def execute_query(
    sql: str
):
    """
    Execute a read-only SQL query against
    the active dataset.
    """

    connection = create_connection()

    try:

        result = connection.execute(
            sql
        ).fetchdf()

        return {
            "success": True,
            "columns": result.columns.tolist(),
            "rows": result.to_dict(
                orient="records"
            )
        }

    except Exception as error:

        return {
            "success": False,
            "error": str(error)
        }

    finally:

        connection.close()