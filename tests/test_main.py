
from io import BytesIO
from pathlib import Path

import pytest

from main import analyze_expenses


PROJECT_ROOT = Path(__file__).resolve().parents[1]


# ----------------------------------------
# TEST 1 — SAMPLE DATA
# ----------------------------------------

def test_sample_expenses():

    csv_path = (
        PROJECT_ROOT / "sample_expenses.csv"
    )

    result = analyze_expenses(csv_path)

    assert result["total_transactions"] == 10

    assert result["total_spending"] == 408.0

    assert (
        result["highest_spending_category"]
        == "Shopping"
    )

    assert (
        result["highest_category_amount"]
        == 200.0
    )

    assert result["spending_by_category"] == {
        "Shopping": 200.0,
        "Food": 114.0,
        "Utilities": 77.0,
        "Transport": 17.0
    }


# ----------------------------------------
# TEST 2 — CSV BYTES
# ----------------------------------------

def test_csv_bytes():

    csv_data = (
        b"category,amount\n"
        b"Food,25\n"
        b"Food,40\n"
        b"Utilities,30\n"
    )

    result = analyze_expenses(
        BytesIO(csv_data)
    )

    assert result["total_transactions"] == 3

    assert result["total_spending"] == 95.0

    assert (
        result["highest_spending_category"]
        == "Food"
    )

    assert (
        result["highest_category_amount"]
        == 65.0
    )


# ----------------------------------------
# TEST INVALID DATA
# ----------------------------------------

@pytest.mark.parametrize(
    "csv_data",
    [
        b"category,amount\n",

        b"description,amount\nTaxi,20\n",

        b"category,amount\n,20\n",

        b"category,amount\nFood,invalid\n",

        b"category,amount\nFood,-25\n"
    ]
)

def test_invalid_csv(csv_data):

    with pytest.raises(ValueError):

        analyze_expenses(
            BytesIO(csv_data)
        )