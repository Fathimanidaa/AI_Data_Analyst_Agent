
import json
import pandas as pd

from services.llm_service import ask_llm
from services.data_tools import (
    get_dataset_profile,
    get_numeric_stat,
    get_group_summary,
    get_top_values,
)


def run_data_agent(df: pd.DataFrame, question: str) -> dict:
    """Choose a safe analysis tool, execute it, and explain its result."""

    if df is None or df.empty:
        return {
            "tool": "none",
            "result": None,
            "answer": "Please upload a non-empty CSV dataset.",
        }

    if not question or not question.strip():
        return {
            "tool": "none",
            "result": None,
            "answer": "Please enter a question.",
        }

    columns = df.columns.astype(str).tolist()

    # Ask the LLM to select a tool and provide its arguments.
    tool_prompt = f"""
You are a tool selector for a data-analysis application.

Choose exactly one tool from:
1. profile
2. numeric_stat
3. group_summary
4. top_values
5. explain

Available dataset columns:
{json.dumps(columns)}

User question:
{question}

Return only a valid JSON object.

For profile:
{{"tool":"profile"}}

For numeric_stat:
{{"tool":"numeric_stat","column":"exact column name",
"operation":"mean"}}

Allowed numeric_stat operations:
mean, median, sum, min, max, count

For group_summary:
{{"tool":"group_summary","group_column":"exact category column",
"value_column":"exact numerical column","operation":"mean"}}

Allowed group_summary operations:
mean, sum, median, count

For top_values:
{{"tool":"top_values","column":"exact column name","n":5}}

For explain:
{{"tool":"explain"}}

Use exact column names from the supplied list.
Never invent a column name.
If the question cannot be mapped confidently to a tool,
choose explain.
"""

    selection = ask_llm(tool_prompt)

    try:
        # Extract the JSON object from the model response.
        start = selection.find("{")
        end = selection.rfind("}") + 1

        if start < 0 or end <= start:
            raise ValueError("No JSON object found.")

        plan = json.loads(selection[start:end])

    except (ValueError, json.JSONDecodeError):
        return {
            "tool": "none",
            "result": None,
            "answer": (
                "I couldn't interpret that request reliably. "
                "Try asking about an average, total, category comparison, "
                "most frequent values, or dataset profile."
            ),
        }

    tool = plan.get("tool")

    try:
        if tool == "profile":
            result = get_dataset_profile(df)

        elif tool == "numeric_stat":
            result = get_numeric_stat(
                df,
                str(plan.get("column", "")),
                str(plan.get("operation", "")),
            )

        elif tool == "group_summary":
            result = get_group_summary(
                df,
                str(plan.get("group_column", "")),
                str(plan.get("value_column", "")),
                str(plan.get("operation", "mean")),
            )

        elif tool == "top_values":
            result = get_top_values(
                df,
                str(plan.get("column", "")),
                int(plan.get("n", 5)),
            )

        elif tool == "explain":
            return {
                "tool": "explain",
                "result": None,
                "answer": ask_llm(question),
            }

        else:
            raise ValueError("The AI selected an unsupported tool.")

    except (ValueError, TypeError, KeyError) as error:
        return {
            "tool": str(tool),
            "result": None,
            "answer": (
                f"I couldn't perform that analysis: {error}\n\n"
                f"Available columns: {', '.join(columns)}"
            ),
        }

    # Let the LLM explain the actual computed result.
    explanation_prompt = f"""
You are a beginner-friendly data analyst.

Answer the user's question using the verified calculation below.
The calculation was performed by Python on the uploaded dataset.

User question:
{question}

Analysis tool:
{tool}

Calculated result:
{json.dumps(result, default=str)}

Explain the result clearly in simple English.
Do not change, invent, or contradict the calculated values.
If the result does not fully answer the question, say so.
"""

    answer = ask_llm(explanation_prompt)

    return {
        "tool": tool,
        "result": result,
        "answer": answer,
    }
