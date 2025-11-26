import pandas as pd
from datetime import datetime

# --- Database File Paths ---
TRANSACTIONS_FILE = "database/transactions.txt"
BUDGETS_FILE = "database/budgets.txt"

def load_transactions():
    """Loads all transactions from the text file into a pandas DataFrame."""
    try:
        df = pd.read_csv(
            TRANSACTIONS_FILE,
            names=["Date", "Type", "Category", "AmountPaisa", "Description"]
        )
        # Ensure 'Amount' is numeric, coerce errors will turn non-numerics into NaT
        df['Amount'] = pd.to_numeric(df['AmountPaisa'], errors='coerce') / 100
        # Drop rows where Amount could not be parsed
        df.dropna(subset=['Amount'], inplace=True)
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=["Date", "Type", "Category", "AmountPaisa", "Description", "Amount"])
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=["Date", "Type", "Category", "AmountPaisa", "Description", "Amount"])

def load_budgets():
    """Loads budgets from the text file into a dictionary."""
    budgets = {}
    try:
        with open(BUDGETS_FILE, "r") as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split(',')
                    if len(parts) == 2:
                        category, amount_paisa = parts
                        budgets[category] = int(amount_paisa) / 100
    except FileNotFoundError:
        pass
    return budgets

def get_spending_for_month(month_to_analyze: str):
    """
    Calculates spending per category for a specific month from the transactions file.
    
    Args:
        month_to_analyze (str): The month in "YYYY-MM" format.

    Returns:
        dict: A dictionary with categories as keys and spent amounts as values.
    """
    transactions_df = load_transactions()
    if transactions_df.empty:
        return {}

    # Filter for expenses in the given month
    monthly_expenses = transactions_df[
        (transactions_df['Type'] == 'Expense') &
        (transactions_df['Date'].str.startswith(month_to_analyze))
    ]
    
    # Calculate spending per category
    expense_by_cat = monthly_expenses.groupby('Category')['Amount'].sum().to_dict()
    
    return expense_by_cat
