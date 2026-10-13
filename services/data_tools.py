
import pandas as pd


def get_dataset_profile(df: pd.DataFrame) -> dict:
    """Return a basic profile of the uploaded dataset."""

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": df.columns.astype(str).tolist(),
        "missing_values": df.isnull().sum().to_dict(),
        "duplicate_rows": int(df.duplicated().sum()),
        "numeric_columns": (
            df.select_dtypes(include="number")
            .columns.astype(str)
            .tolist()
        ),
    }


def get_numeric_stat(
    df: pd.DataFrame,
    column: str,
    operation: str,
) -> dict:
    """Calculate a statistic for a numerical column."""

    if column not in df.columns:
        raise ValueError(f"Column not found: {column}")

    if not pd.api.types.is_numeric_dtype(df[column]):
        raise ValueError(f"{column} is not a numerical column.")

    values = df[column].dropna()

    if values.empty:
        raise ValueError(f"{column} contains no valid numerical values.")

    operations = {
        "mean": values.mean,
        "median": values.median,
        "sum": values.sum,
        "min": values.min,
        "max": values.max,
        "count": values.count,
    }

    if operation not in operations:
        raise ValueError(
            "Supported operations: mean, median, sum, min, max, count."
        )

    result = operations[operation]()

    return {
        "column": str(column),
        "operation": operation,
        "result": float(result),
    }


def get_group_summary(
    df: pd.DataFrame,
    group_column: str,
    value_column: str,
    operation: str = "mean",
) -> dict:
    """Summarise a numerical column by category."""

    if group_column not in df.columns:
        raise ValueError(f"Column not found: {group_column}")

    if value_column not in df.columns:
        raise ValueError(f"Column not found: {value_column}")

    if not pd.api.types.is_numeric_dtype(df[value_column]):
        raise ValueError(f"{value_column} must be numerical.")

    if operation not in ["mean", "sum", "median", "count"]:
        raise ValueError(
            "Supported operations: mean, sum, median, count."
        )

    grouped = df.groupby(
        group_column,
        dropna=False,
    )[value_column]

    result = getattr(grouped, operation)()

    return {
        "group_column": str(group_column),
        "value_column": str(value_column),
        "operation": operation,
        "results": {
            str(key): float(value)
            for key, value in result.items()
        },
    }


def get_top_values(
    df: pd.DataFrame,
    column: str,
    n: int = 5,
) -> dict:
    """Return the most frequent values in a column."""

    if column not in df.columns:
        raise ValueError(f"Column not found: {column}")

    if not 1 <= n <= 20:
        raise ValueError("n must be between 1 and 20.")

    result = df[column].value_counts(
        dropna=False
    ).head(n)

    return {
        "column": str(column),
        "top_values": {
            str(key): int(value)
            for key, value in result.items()
        },
    }
