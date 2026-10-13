
import streamlit as st
import pandas as pd
from services.llm_service import ask_llm
from services.agent_service import run_data_agent


# =========================================================
# 1. PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="AI Data Analyst Agent",
    page_icon="📊",
    layout="wide",
)

st.title("📊 AI Data Analyst Agent")
st.write(
    "Upload a CSV file to explore, analyse, visualise, "
    "clean, and understand your data using AI."
)


# =========================================================
# 2. CSV UPLOAD
# =========================================================

uploaded_file = st.file_uploader(
    "Upload your CSV file",
    type=["csv"],
)

df = None

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        if len(df.columns) == 0:
            st.warning("The uploaded CSV has no columns.")
            df = None
        elif df.empty:
            st.warning("The CSV contains no data rows.")
        else:
            st.success("CSV file uploaded successfully!")

    except Exception as exc:
        st.error(f"Could not read the CSV file: {exc}")
        df = None


# =========================================================
# 3. DATASET ANALYSIS
# =========================================================

if df is not None:

    numeric_df = df.select_dtypes(include="number")

    # -----------------------------------------------------
    # 3.1 Dataset overview
    # -----------------------------------------------------

    st.header("1. Dataset Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Rows", f"{len(df):,}")
    col2.metric("Total Columns", f"{len(df.columns):,}")
    col3.metric(
        "Missing Values",
        f"{int(df.isnull().sum().sum()):,}",
    )
    col4.metric(
        "Duplicate Rows",
        f"{int(df.duplicated().sum()):,}",
    )

    # -----------------------------------------------------
    # 3.2 Data preview
    # -----------------------------------------------------

    with st.expander("2. Data Preview", expanded=True):
        st.dataframe(
            df.head(10),
            use_container_width=True,
        )

    # -----------------------------------------------------
    # 3.3 Column information
    # -----------------------------------------------------

    with st.expander("3. Column Information"):

        column_info = pd.DataFrame({
            "Column Name": df.columns.astype(str),
            "Data Type": df.dtypes.astype(str).values,
            "Missing Values": df.isnull().sum().values,
            "Missing (%)": (
                df.isnull().mean().mul(100).round(2).values
            ),
            "Unique Values": df.nunique().values,
        })

        st.dataframe(
            column_info,
            use_container_width=True,
        )

        profile_csv = column_info.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            "Download Column Profile as CSV",
            data=profile_csv,
            file_name="data_profile.csv",
            mime="text/csv",
            key="download_profile",
        )

    # -----------------------------------------------------
    # 3.4 Missing-value analysis
    # -----------------------------------------------------

    with st.expander("4. Missing-Value Analysis"):

        missing_info = (
            df.isnull()
            .sum()
            .rename_axis("Column")
            .reset_index(name="Missing Values")
        )

        missing_info = missing_info[
            missing_info["Missing Values"] > 0
        ]

        if missing_info.empty:
            st.success("There are no missing values.")
        else:
            st.dataframe(
                missing_info,
                use_container_width=True,
            )

            st.bar_chart(
                missing_info.set_index("Column")
            )

    # -----------------------------------------------------
    # 3.5 Numerical summary
    # -----------------------------------------------------

    with st.expander("5. Numerical Summary"):

        if numeric_df.empty:
            st.info("No numerical columns were found.")
        else:
            st.dataframe(
                numeric_df.describe().round(2),
                use_container_width=True,
            )

    # -----------------------------------------------------
  
    # -----------------------------------------------------
    # 3.6 Interactive charts
    # -----------------------------------------------------

    with st.expander("6. Create a Chart"):

        if df.empty:
            st.warning("There is no data available to chart.")

        elif not df.columns.is_unique:
            st.error(
                "Your CSV contains duplicate column names. "
                "Please rename them before creating a chart."
            )

        else:
            chart_type = st.selectbox(
                "Choose a chart type",
                ["Bar Chart", "Line Chart", "Histogram"],
                key="chart_type",
            )

            if chart_type == "Histogram":

                if numeric_df.empty:
                    st.warning(
                        "A histogram requires a numerical column."
                    )
                else:
                    selected_column = st.selectbox(
                        "Select a numerical column",
                        numeric_df.columns.tolist(),
                        key="histogram_column",
                    )

                    values = pd.to_numeric(
                        df[selected_column],
                        errors="coerce",
                    ).dropna()

                    if values.empty:
                        st.warning(
                            "No valid numerical values are available."
                        )
                    else:
                        histogram = pd.cut(
                            values,
                            bins=10,
                        ).value_counts(sort=False)

                        st.bar_chart(histogram)

            else:
                if len(df.columns) < 2:
                    st.warning(
                        "At least two columns are required for this chart."
                    )

                elif numeric_df.empty:
                    st.warning(
                        "Bar and line charts require a numerical column."
                    )

                else:
                    x_column = st.selectbox(
                        "Select the X-axis column",
                        df.columns.tolist(),
                        key="chart_x_column",
                    )

                    y_column = st.selectbox(
                        "Select the numerical Y-axis column",
                        numeric_df.columns.tolist(),
                        key="chart_y_column",
                    )

                    if x_column == y_column:
                        st.warning(
                            "Please select different columns "
                            "for the X-axis and Y-axis."
                        )

                    else:
                        chart_data = df[
                            [x_column, y_column]
                        ].copy()

                        chart_data[y_column] = pd.to_numeric(
                            chart_data[y_column],
                            errors="coerce",
                        )

                        chart_data = chart_data.dropna(
                            subset=[x_column, y_column]
                        )

                        if chart_data.empty:
                            st.warning(
                                "No valid data is available for this chart."
                            )
                        else:
                            chart_data = chart_data.groupby(
                                x_column
                            )[y_column].sum()

                            if chart_type == "Bar Chart":
                                st.bar_chart(chart_data)
                            else:
                                st.line_chart(chart_data)

    # -----------------------------------------------------
    # 3.7 Data cleaning assistant
    # -----------------------------------------------------

    with st.expander("7. Data Cleaning Assistant", expanded=True):

        st.write(
            "Select cleaning operations, preview the results, "
            "and download a cleaned copy. Your original dataset "
            "will not be modified."
        )

        remove_duplicates = st.checkbox(
            "Remove duplicate rows",
            value=False,
            key="remove_duplicates",
        )

        missing_option = st.selectbox(
            "How should missing values be handled?",
            [
                "Keep missing values",
                "Remove rows with missing values",
                "Fill numerical missing values with the median",
            ],
            key="missing_option",
        )

        cleaned_df = df.copy()
        original_rows = len(cleaned_df)

        if remove_duplicates:
            cleaned_df = cleaned_df.drop_duplicates()

        if missing_option == "Remove rows with missing values":
            cleaned_df = cleaned_df.dropna()

        elif (
            missing_option
            == "Fill numerical missing values with the median"
        ):

            numeric_columns = cleaned_df.select_dtypes(
                include="number"
            ).columns

            for column in numeric_columns:
                median_value = cleaned_df[column].median()

                if pd.notna(median_value):
                    cleaned_df[column] = cleaned_df[column].fillna(
                        median_value
                    )

        st.subheader("Cleaning Summary")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Original Rows",
            f"{original_rows:,}",
        )

        col2.metric(
            "Cleaned Rows",
            f"{len(cleaned_df):,}",
        )

        col3.metric(
            "Rows Removed",
            f"{original_rows - len(cleaned_df):,}",
        )

        st.write("**Cleaned Data Preview**")

        st.dataframe(
            cleaned_df.head(10),
            use_container_width=True,
        )

        cleaned_csv = cleaned_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            "Download Cleaned Dataset",
            data=cleaned_csv,
            file_name="cleaned_dataset.csv",
            mime="text/csv",
            key="download_cleaned",
        )

    # -----------------------------------------------------
    # 3.8 Rule-based question assistant
    # -----------------------------------------------------

    with st.expander("8. Quick Questions About Your Data"):

        question = st.text_input(
            "Ask a question about the dataset",
            placeholder="How many rows are in this dataset?",
            key="quick_question",
        )

        if question:
            q = question.lower().strip()
            numeric_columns = numeric_df.columns.tolist()

            if "missing" in q or "null" in q:

                missing = df.isnull().sum()
                missing = missing[missing > 0]

                if missing.empty:
                    st.success("There are no missing values.")
                else:
                    st.write("Missing values by column:")

                    st.dataframe(
                        missing.rename(
                            "Missing Values"
                        ).reset_index().rename(
                            columns={"index": "Column"}
                        ),
                        use_container_width=True,
                    )

            elif "duplicate" in q:
                st.write(
                    f"Duplicate rows: {int(df.duplicated().sum()):,}"
                )

            elif "row" in q:
                st.write(f"Total rows: {len(df):,}")

            elif "column" in q:
                st.write(f"Total columns: {len(df.columns):,}")
                st.write(
                    "Column names:",
                    ", ".join(map(str, df.columns)),
                )

            elif any(
                word in q
                for word in [
                    "average", "mean", "median",
                    "sum", "total", "maximum", "minimum",
                    "highest", "lowest",
                ]
            ):

                if not numeric_columns:
                    st.warning(
                        "No numerical columns are available."
                    )

                else:
                    matched_column = next(
                        (
                            column
                            for column in numeric_columns
                            if str(column).lower() in q
                        ),
                        None,
                    )

                    if matched_column is None:
                        st.info(
                            "Include a numerical column name "
                            "in your question."
                        )
                        st.write(
                            "Available numerical columns:",
                            ", ".join(map(str, numeric_columns)),
                        )

                    else:
                        values = pd.to_numeric(
                            df[matched_column],
                            errors="coerce",
                        ).dropna()

                        if values.empty:
                            st.info(
                                "No valid numerical values were found."
                            )

                        elif "median" in q:
                            st.write(
                                f"Median: {values.median():,.2f}"
                            )

                        elif "average" in q or "mean" in q:
                            st.write(
                                f"Average: {values.mean():,.2f}"
                            )

                        elif "sum" in q or "total" in q:
                            st.write(
                                f"Sum: {values.sum():,.2f}"
                            )

                        elif "maximum" in q or "highest" in q:
                            st.write(
                                f"Maximum: {values.max():,.2f}"
                            )

                        elif "minimum" in q or "lowest" in q:
                            st.write(
                                f"Minimum: {values.min():,.2f}"
                            )

                        else:
                            st.write(
                                f"Average: {values.mean():,.2f}"
                            )

            else:
                st.info(
                    "Try asking about rows, columns, missing values, "
                    "duplicates, or numerical statistics."
                )



# =========================================================
# 4. AI DATA ANALYST AGENT
# =========================================================

st.divider()
st.header("🤖 AI Data Analyst Agent")

st.write(
    "Ask questions about your uploaded dataset. "
    "The agent can select analysis tools, calculate results "
    "using Python, and explain the findings."
)

agent_question = st.text_area(
    "Enter your question",
    placeholder=(
        "Examples:\n"
        "- What is the average sales?\n"
        "- Which product has the highest total sales?\n"
        "- Show the most frequent customer categories.\n"
        "- Give me an overview of this dataset."
    ),
    key="agent_question",
)

if st.button("Analyse with AI Agent", key="run_agent"):

    if not agent_question.strip():
        st.warning("Please enter a question.")

    elif df is None:
        st.warning("Please upload a CSV dataset first.")

    else:
        with st.spinner("Analysing your question..."):
            response = run_data_agent(df, agent_question)

        st.subheader("Agent Answer")
        st.markdown(response["answer"])

        if response.get("result") is not None:
            with st.expander("View calculation details"):
                st.write("**Selected tool:**", response["tool"])
                st.json(response["result"])


# =========================================================
# 5. FOOTER
# =========================================================

st.divider()

st.caption(
    "AI Data Analyst Agent | Built with Streamlit, Pandas, and an LLM"
)
