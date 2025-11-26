import streamlit as st
from datetime import datetime
import pandas as pd
from features.common.utils import load_transactions, load_budgets

# --- Page Configuration ---
st.set_page_config(
    page_title="Personal Finance Dashboard",
    page_icon="💰",
    layout="wide",
)

# --- Main Dashboard ---

def main():
    """Main function to render the Streamlit dashboard."""

    # --- Custom CSS for Styling ---
    st.markdown("""
    <style>
        /* General body styling */
        body {
            font-family: Arial, sans-serif;
        }
        /* Main container styling */
        .main .block-container {
            max-width: 1200px;
            padding: 2rem 1rem;
        }
        /* Card-like containers for sections */
        .st-emotion-cache-1y4p8pa {
            border-radius: 10px;
            box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
            transition: 0.3s;
            padding: 20px;
            background-color: white;
            margin-bottom: 20px;
        }
        .st-emotion-cache-1y4p8pa:hover {
            box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2);
        }
        /* Style for headers */
        h1, h2, h3 {
            color: #333;
        }
        /* Metric styling */
        .st-emotion-cache-1vze3d2 {
             text-align: center;
        }
    </style>
    """, unsafe_allow_html=True)

    st.title("💰 Personal Finance Dashboard")

    # Load data
    transactions_df = load_transactions()
    budgets = load_budgets()

    if transactions_df.empty:
        st.warning("No transaction data found. Please add transactions in the CLI.")
        return

    # --- Balance Section ---
    with st.container():
        st.header("Current Balance")
        total_income = transactions_df[transactions_df['Type'] == 'Income']['Amount'].sum()
        total_expense = transactions_df[transactions_df['Type'] == 'Expense']['Amount'].sum()
        balance = total_income - total_expense

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Income", f"Rs {total_income:,.2f}")
        col2.metric("Total Expense", f"Rs {total_expense:,.2f}")
        col3.metric("Current Balance", f"Rs {balance:,.2f}")

    st.markdown("---")

    # --- Budget Status Section ---
    with st.container():
        st.header("Budget Status (Current Month)")
        if not budgets:
            st.info("No budgets set. Use the CLI to set budgets.")
        else:
            current_month = datetime.now().strftime("%Y-%m")
            monthly_expenses = transactions_df[
                (transactions_df['Type'] == 'Expense') &
                (transactions_df['Date'].str.startswith(current_month))
            ]
            expense_by_cat = monthly_expenses.groupby('Category')['Amount'].sum()

            for category, budget_amount in budgets.items():
                spent_amount = expense_by_cat.get(category, 0)
                percentage = (spent_amount / budget_amount) * 100 if budget_amount > 0 else 0
                
                st.subheader(category)
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.progress(min(int(percentage), 100))
                with col2:
                    status_color = "red" if percentage > 100 else "orange" if percentage >= 70 else "green"
                    status_text = "OVER" if percentage > 100 else "Warning" if percentage >= 70 else "OK"
                    st.markdown(f"**<font color='{status_color}'>{status_text}</font>**", unsafe_allow_html=True)

                st.text(f"Spent: Rs {spent_amount:,.2f} / Budget: Rs {budget_amount:,.2f}")
                st.text("")

    st.markdown("---")

    # --- Recent Transactions Table ---
    with st.container():
        st.header("Recent Transactions")
        
        def style_transactions(df):
            def row_styler(row):
                if row.Type == 'Income': return ['background-color: #d4edda'] * len(row)
                if row.Type == 'Expense': return ['background-color: #f8d7da'] * len(row)
                return [''] * len(row)
            
            display_df = df[['Date', 'Type', 'Category', 'Description', 'Amount']].copy()
            display_df['Amount'] = display_df['Amount'].apply(lambda x: f"Rs {x:,.2f}")
            return display_df.tail(10).style.apply(row_styler, axis=1)

        styler = style_transactions(transactions_df)
        st.dataframe(styler, use_container_width=True)


if __name__ == "__main__":
    main()
