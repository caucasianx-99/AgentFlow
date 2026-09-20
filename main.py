
import json
import math
from pathlib import Path

import pandas as pd


def analyze_expenses(csv_path):
    """
    Analyze an expenses CSV.

    Required columns:
        category
        amount

    Returns:
        A dictionary containing total spending,
        transaction count, category totals,
        and the highest spending category.
    """

    # ----------------------------------------
    # READ CSV
    # ----------------------------------------

    try:
        data = pd.read_csv(csv_path)

    except pd.errors.EmptyDataError as error:
        raise ValueError(
            "The CSV file is empty."
        ) from error

    except UnicodeDecodeError as error:
        raise ValueError(
            "The CSV file must use UTF-8 encoding."
        ) from error

    # ----------------------------------------
    # VALIDATE DATA
    # ----------------------------------------

    required_columns = {
        "category",
        "amount"
    }

    missing_columns = (
        required_columns - set(data.columns)
    )

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    if data.empty:
        raise ValueError(
            "The CSV contains no transactions."
        )

    # ----------------------------------------
    # VALIDATE CATEGORIES
    # ----------------------------------------

    data["category"] = (
        data["category"]
        .astype("string")
        .str.strip()
    )

    invalid_categories = (
        data["category"].isna()
        | data["category"].eq("")
    )

    if invalid_categories.any():
        raise ValueError(
            "Every transaction must have "
            "a valid category."
        )

    # ----------------------------------------
    # VALIDATE AMOUNTS
    # ----------------------------------------

    data["amount"] = pd.to_numeric(
        data["amount"],
        errors="coerce"
    )

    if data["amount"].isna().any():
        raise ValueError(
            "Every amount must be numeric."
        )

    if not all(
        math.isfinite(float(amount))
        for amount in data["amount"]
    ):
        raise ValueError(
            "Amounts must be finite numbers."
        )

    if (data["amount"] < 0).any():
        raise ValueError(
            "Expense amounts cannot be negative."
        )

    # ----------------------------------------
    # CALCULATE TOTALS
    # ----------------------------------------

    totals = (
        data.groupby("category")["amount"]
        .sum()
        .sort_values(
            ascending=False,
            kind="stable"
        )
    )

    # ----------------------------------------
    # BUILD STRUCTURED RESULT
    # ----------------------------------------

    result = {
        "total_transactions": len(data),

        "total_spending": round(
            float(data["amount"].sum()),
            2
        ),

        "spending_by_category": {
            category: round(float(amount), 2)
            for category, amount in totals.items()
        },

        "highest_spending_category": (
            str(totals.index[0])
        ),

        "highest_category_amount": round(
            float(totals.iloc[0]),
            2
        )
    }

    return result


# ----------------------------------------
# TERMINAL TEST
# ----------------------------------------

if __name__ == "__main__":

    csv_file = (
        Path(__file__).parent
        / "sample_expenses.csv"
    )

    analysis = analyze_expenses(
        csv_file
    )

    print(
        json.dumps(
            analysis,
            indent=4
        )
    )