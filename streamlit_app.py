import tempfile

import pandas as pd
import streamlit as st

from app.graph.analyst_graph import analyst_graph
from app.tools.chart_tools import create_chart
from app.tools.database_tools import set_dataset_path
from app.data.loader import load_dataset


st.set_page_config(
    page_title="AI Data Analyst Agent",
    page_icon="📊",
    layout="wide",
)


# ==================================================
# SESSION STATE
# ==================================================

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if "dataset_path" not in st.session_state:
    st.session_state.dataset_path = "data/sales.csv"

if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None


# ==================================================
# HEADER
# ==================================================

st.title("📊 AI Data Analyst Agent")

st.markdown(
    """
    Ask business questions in natural language.

    The system automatically:

    - understands your analytical intent
    - generates SQL
    - validates SQL for safety
    - executes queries with DuckDB
    - analyzes the results
    - selects an appropriate visualization
    """
)

st.divider()


# ==================================================
# DATASET UPLOAD
# ==================================================

st.header("📁 Dataset")

uploaded_file = st.file_uploader(
    "Upload a CSV file",
    type=["csv"],
    help=(
        "Upload your own dataset or leave this empty "
        "to use the built-in sales demo dataset."
    ),
)


if uploaded_file is not None:

    if (
        st.session_state.uploaded_file_name
        != uploaded_file.name
    ):

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".csv"
        ) as temp_file:

            temp_file.write(
                uploaded_file.getvalue()
            )

            st.session_state.dataset_path = (
                temp_file.name
            )

        st.session_state.uploaded_file_name = (
            uploaded_file.name
        )

        st.session_state.last_result = None

else:

    st.session_state.dataset_path = (
        "data/sales.csv"
    )

    st.session_state.uploaded_file_name = None


set_dataset_path(
    st.session_state.dataset_path
)


# ==================================================
# DATASET PREVIEW
# ==================================================

try:

    preview_df = load_dataset(
        st.session_state.dataset_path
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Rows",
            len(preview_df)
        )

    with col2:
        st.metric(
            "Columns",
            len(preview_df.columns)
        )

    with col3:
        st.metric(
            "Dataset",
            (
                uploaded_file.name
                if uploaded_file is not None
                else "Demo sales.csv"
            )
        )


    with st.expander(
        "👀 Preview Dataset",
        expanded=False
    ):

        st.dataframe(
            preview_df.head(20),
            use_container_width=True,
            hide_index=True
        )


    with st.expander(
        "🧬 Dataset Schema",
        expanded=False
    ):

        schema_df = pd.DataFrame(
            {
                "Column": preview_df.columns,
                "Type": [
                    str(dtype)
                    for dtype
                    in preview_df.dtypes
                ]
            }
        )

        st.dataframe(
            schema_df,
            use_container_width=True,
            hide_index=True
        )


except Exception as error:

    st.error(
        "The CSV dataset could not be read."
    )

    with st.expander(
        "Technical details"
    ):
        st.code(
            str(error)
        )

    st.stop()


st.divider()


# ==================================================
# EXAMPLE QUESTIONS
# ==================================================

with st.expander(
    "💡 Example questions",
    expanded=False
):

    st.markdown(
        """
        **Demo sales dataset**

        - `Which category generated the most revenue?`
        - `Show total revenue for each region from highest to lowest.`
        - `Which customer generated the most revenue?`
        - `Show monthly revenue over time.`
        - `Compare total revenue by product category.`
        - `What are the top 5 products by revenue?`

        **For uploaded datasets**

        You can ask questions using the columns available
        in the uploaded CSV.
        """
    )


# ==================================================
# QUESTION INPUT
# ==================================================

question = st.text_area(
    "Ask a data question",
    placeholder=(
        "Example: Show total revenue for each region "
        "from highest to lowest."
    ),
    height=110,
)


run_button = st.button(
    "🚀 Analyze Data",
    type="primary",
    use_container_width=True,
)


# ==================================================
# RUN ANALYST GRAPH
# ==================================================

if run_button:

    if not question.strip():

        st.error(
            "Please enter a data analysis question."
        )

    else:

        initial_state = {
            "question": question.strip(),
            "plan": {},
            "sql_result": {},
            "analysis": "",
            "visualization": {},
            "final_response": ""
        }

        try:

            with st.spinner(
                "AI agents are analyzing your data..."
            ):

                set_dataset_path(
                    st.session_state.dataset_path
                )

                result = analyst_graph.invoke(
                    initial_state
                )

            result["question"] = question.strip()

            st.session_state.last_result = result

        except Exception as error:

            st.error(
                "An error occurred while analyzing the data."
            )

            with st.expander(
                "Technical details"
            ):
                st.code(
                    str(error)
                )


# ==================================================
# DISPLAY RESULTS
# ==================================================

result = st.session_state.last_result


if result:

    sql_result = result.get(
        "sql_result",
        {}
    )

    rows = sql_result.get(
        "rows",
        []
    )

    visualization = result.get(
        "visualization",
        {}
    )

    st.divider()


    # ==================================================
    # AI INSIGHT
    # ==================================================

    st.header(
        "🧠 AI Insight"
    )

    st.markdown(
        result.get(
            "analysis",
            "No analysis available."
        )
    )


    # ==================================================
    # VISUALIZATION
    # ==================================================

    st.divider()

    st.header(
        "📈 Visualization"
    )

    chart_type = visualization.get(
        "chart_type",
        "none"
    )

    if (
        rows
        and chart_type != "none"
    ):

        x_column = visualization.get(
            "x"
        )

        y_column = visualization.get(
            "y"
        )

        available_columns = (
            sql_result.get(
                "columns",
                []
            )
        )

        if (
            x_column in available_columns
            and y_column in available_columns
        ):

            chart = create_chart(
                rows=rows,
                chart_type=chart_type,
                x=x_column,
                y=y_column,
                title=visualization.get(
                    "title",
                    "Data Visualization"
                )
            )

            if chart is not None:

                st.plotly_chart(
                    chart,
                    use_container_width=True
                )

            else:

                st.info(
                    "No chart was generated "
                    "for this result."
                )

        else:

            st.warning(
                "The visualization agent selected "
                "columns that are not present "
                "in the query result."
            )

    else:

        st.info(
            "No visualization was recommended "
            "for this result."
        )


    # ==================================================
    # DATA RESULTS
    # ==================================================

    st.divider()

    st.header(
        "📋 Data Results"
    )

    if rows:

        dataframe = pd.DataFrame(
            rows
        )

        st.dataframe(
            dataframe,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.warning(
            "The query returned no rows."
        )


    # ==================================================
    # EXPORT RESULTS
    # ==================================================

    st.divider()

    st.header(
        "⬇️ Export Results"
    )

    if rows:

        export_df = pd.DataFrame(
            rows
        )

        csv_data = export_df.to_csv(
            index=False
        ).encode(
            "utf-8"
        )

        report_text = f"""
AI DATA ANALYST REPORT

Question:
{result.get("question", "")}

Analysis:
{result.get("analysis", "")}

Generated SQL:
{sql_result.get("sql", "")}

Rows Returned:
{len(rows)}

Visualization:
{visualization.get("chart_type", "none")}

Visualization Title:
{visualization.get("title", "")}

Dataset:
{st.session_state.uploaded_file_name or "Demo sales.csv"}
""".strip()

        download_col1, download_col2 = (
            st.columns(2)
        )

        with download_col1:

            st.download_button(
                label="📥 Download Results CSV",
                data=csv_data,
                file_name="analysis_results.csv",
                mime="text/csv",
                use_container_width=True
            )

        with download_col2:

            st.download_button(
                label="📄 Download Analysis Report",
                data=report_text,
                file_name="analysis_report.txt",
                mime="text/plain",
                use_container_width=True
            )

    else:

        st.info(
            "There are no query results to export."
        )


    # ==================================================
    # METRICS
    # ==================================================

    st.divider()

    metric1, metric2, metric3 = (
        st.columns(3)
    )

    with metric1:

        st.metric(
            "Rows Returned",
            len(rows)
        )

    with metric2:

        st.metric(
            "Analysis Intent",
            result.get(
                "plan",
                {}
            ).get(
                "intent",
                "-"
            )
        )

    with metric3:

        st.metric(
            "Chart Type",
            visualization.get(
                "chart_type",
                "none"
            )
        )


    # ==================================================
    # AGENT EXECUTION DETAILS
    # ==================================================

    st.divider()

    with st.expander(
        "⚙️ Agent Execution Details",
        expanded=False
    ):

        st.subheader(
            "🧠 Planner Agent"
        )

        st.json(
            result.get(
                "plan",
                {}
            )
        )


        st.subheader(
            "🗄️ Generated SQL"
        )

        generated_sql = (
            sql_result.get(
                "sql",
                ""
            )
        )

        if generated_sql:

            st.code(
                generated_sql,
                language="sql"
            )

        else:

            st.write(
                "No SQL query was generated."
            )


        st.subheader(
            "🛡️ SQL Safety Validation"
        )

        st.json(
            sql_result.get(
                "validation",
                {}
            )
        )


        st.subheader(
            "📊 Visualization Agent"
        )

        st.json(
            visualization
        )


        st.subheader(
            "📁 Active Dataset"
        )

        st.write(
            st.session_state.uploaded_file_name
            or "Demo sales.csv"
        )


# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:

    st.title(
        "📊 Analytics System"
    )

    st.markdown(
        """
        **AI Data Analyst Agent**

        Powered by:

        - 🧠 Planner Agent
        - 🗄️ SQL Agent
        - 🛡️ SQL Safety Validator
        - 🦆 DuckDB
        - 📈 Visualization Agent
        - 🤖 Groq LLM
        """
    )

    st.divider()

    st.subheader(
        "Active Dataset"
    )

    if (
        st.session_state.uploaded_file_name
        is not None
    ):

        st.success(
            st.session_state.uploaded_file_name
        )

    else:

        st.info(
            "Demo sales.csv"
        )


    st.divider()

    st.subheader(
        "Architecture"
    )

    st.markdown(
        """
        `CSV Dataset`

        ↓

        **Schema Inspector**

        ↓

        `Natural Language Question`

        ↓

        **Planner Agent**

        ↓

        **SQL Agent**

        ↓

        **SQL Validator**

        ↓

        **DuckDB**

        ↓

        **Analysis Agent**

        ↓

        **Visualization Agent**
        """
    )

    st.divider()

    if st.button(
        "🗑️ Clear Results",
        use_container_width=True
    ):

        st.session_state.last_result = None

        st.rerun()