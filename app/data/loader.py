import pandas as pd


DEFAULT_CSV_PATH = "data/sales.csv"


def load_dataset(
    csv_path: str = DEFAULT_CSV_PATH
) -> pd.DataFrame:
    """
    Load a CSV dataset into a pandas DataFrame.
    """

    df = pd.read_csv(csv_path)

    for column in df.columns:

        column_lower = column.lower()

        if (
            "date" in column_lower
            or "time" in column_lower
        ):

            try:
                df[column] = pd.to_datetime(
                    df[column]
                )

            except (ValueError, TypeError):
                pass

    return df


def load_sales_data(
    csv_path: str = DEFAULT_CSV_PATH
) -> pd.DataFrame:

    return load_dataset(csv_path)