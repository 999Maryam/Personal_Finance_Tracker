import questionary
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress_bar import ProgressBar
from datetime import datetime
import calendar
from features.common.utils import load_transactions, load_budgets

# Initialize Rich Console
console = Console()

def generate_monthly_report():
    """Generates a financial report for a user-specified month."""
    console.print("\n[bold blue]-- Generate Monthly Financial Report --[/bold blue]")

    current_month_str = datetime.now().strftime("%Y-%m")
    month_to_analyze = questionary.text(
        "Enter the month to analyze (e.g., YYYY-MM):",
        default=current_month_str
    ).ask()

    if not month_to_analyze:
        console.print("[bold red]Month not provided. Aborting.[/bold red]")
        return

    try:
        datetime.strptime(month_to_analyze, "%Y-%m")
    except ValueError:
        console.print("[bold red]Invalid format. Please use YYYY-MM.[/bold red]")
        return

    transactions_df = load_transactions()
    monthly_df = transactions_df[transactions_df['Date'].str.startswith(month_to_analyze)]

    if monthly_df.empty:
        console.print(f"[bold]No transactions found for {month_to_analyze}.[/bold]")
        return

    total_income = monthly_df[monthly_df['Type'] == 'Income']['Amount'].sum()
    total_expense = monthly_df[monthly_df['Type'] == 'Expense']['Amount'].sum()
    net_savings = total_income - total_expense

    summary_text = (
        f"Total Income:  [bold green]{total_income:.2f}[/bold green]\n"
        f"Total Expense: [bold red]{total_expense:.2f}[/bold red]\n"
        f"Net Savings:   [bold cyan]{net_savings:.2f}[/bold cyan]"
    )
    console.print(Panel(summary_text, title=f"[bold]Financial Summary for {month_to_analyze}[/bold]", expand=False))

    expense_by_category = monthly_df[monthly_df['Type'] == 'Expense'].groupby('Category')['Amount'].sum()

    if not expense_by_category.empty:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Expense Category", style="cyan")
        table.add_column("Amount", justify="right")
        table.add_column("% of Total", justify="right")

        sorted_categories = expense_by_category.sort_values(ascending=False)

        for category, amount in sorted_categories.items():
            percentage = (amount / total_expense) * 100 if total_expense > 0 else 0
            table.add_row(category, f"{amount:.2f}", f"{percentage:.1f}%")
        
        console.print("\n[bold]Expense Breakdown[/bold]")
        console.print(table)
    else:
        console.print("\n[bold green]No expenses recorded for this month.[/bold green]")


def spending_analysis():
    """Provides a visual and statistical analysis of spending for a month."""
    console.print("\n[bold blue]-- Spending Analysis --[/bold blue]")

    current_month_str = datetime.now().strftime("%Y-%m")
    month_to_analyze = questionary.text(
        "Enter the month to analyze (e.g., YYYY-MM):",
        default=current_month_str
    ).ask()

    if not month_to_analyze:
        console.print("[bold red]Month not provided. Aborting.[/bold red]")
        return

    transactions_df = load_transactions()
    monthly_df = transactions_df[transactions_df['Date'].str.startswith(month_to_analyze)]
    
    if monthly_df.empty:
        console.print(f"[bold]No transactions found for {month_to_analyze}.[/bold]")
        return

    total_expense = monthly_df[monthly_df['Type'] == 'Expense']['Amount'].sum()
    expense_by_category = monthly_df[monthly_df['Type'] == 'Expense'].groupby('Category')['Amount'].sum()

    if total_expense == 0:
        console.print("[bold green]No expenses to analyze for this month.[/bold green]")
        return

    console.print("\n[bold]Spending by Category (ASCII Chart)[/bold]")
    sorted_categories = expense_by_category.sort_values(ascending=False)
    
    max_len_category = max(len(cat) for cat in sorted_categories.index) if not sorted_categories.empty else 0

    for category, amount in sorted_categories.items():
        percentage = (amount / total_expense) * 100
        bar_length = int(percentage / 2) # Scale to 50 characters max
        bar = '█' * bar_length
        console.print(f"{category.ljust(max_len_category)} | {bar} {percentage:.1f}%")

    console.print("\n[bold]Top 3 Spending Categories[/bold]")
    for i, (category, amount) in enumerate(sorted_categories.head(3).items()):
        console.print(f"{i+1}. {category}: [bold red]{amount:.2f}[/bold red]")

    year, month = map(int, month_to_analyze.split('-'))
    days_in_month = calendar.monthrange(year, month)[1]
    avg_daily_expense = total_expense / days_in_month
    console.print(f"\n[bold]Average Daily Expense:[/bold] [yellow]{avg_daily_expense:.2f}[/yellow]")


def financial_health_score():
    """Calculates and displays a financial health score."""
    console.print("\n[bold blue]-- Financial Health Score --[/bold blue]")

    current_month_str = datetime.now().strftime("%Y-%m")
    month_to_analyze = questionary.text(
        "Enter the month to analyze (e.g., YYYY-MM):",
        default=current_month_str
    ).ask()

    if not month_to_analyze:
        console.print("[bold red]Month not provided. Aborting.[/bold red]")
        return

    transactions_df = load_transactions()
    monthly_df = transactions_df[transactions_df['Date'].str.startswith(month_to_analyze)]

    if monthly_df.empty:
        console.print(f"[bold]No transactions found for {month_to_analyze}.[/bold]")
        return

    total_income = monthly_df[monthly_df['Type'] == 'Income']['Amount'].sum()
    total_expense = monthly_df[monthly_df['Type'] == 'Expense']['Amount'].sum()
    expense_by_category = monthly_df[monthly_df['Type'] == 'Expense'].groupby('Category')['Amount'].sum().to_dict()
    
    savings_rate_score = 0
    if total_income > 0:
        savings_rate = (total_income - total_expense) / total_income
        savings_rate_score = max(0, min(savings_rate / 0.2, 1)) * 60

    budgets = load_budgets()
    budget_adherence_score = 0
    if budgets:
        on_budget_count = 0
        for category, budget_amount in budgets.items():
            spent_amount = expense_by_category.get(category, 0)
            if spent_amount <= budget_amount:
                on_budget_count += 1
        
        if len(budgets) > 0:
            budget_adherence_score = (on_budget_count / len(budgets)) * 40

    total_score = savings_rate_score + budget_adherence_score

    if total_score >= 80:
        interpretation, reco = "[bold green]Excellent! You are managing your finances very well.[/bold green]", "Keep up the great habits. Consider allocating more to investments."
    elif total_score >= 60:
        interpretation, reco = "[bold yellow]Good! You are on the right track.[/bold yellow]", "Focus on increasing your savings rate or sticking closer to your budgets."
    elif total_score >= 40:
        interpretation, reco = "[bold orange3]Needs Improvement. There are areas to work on.[/bold orange3]", "Create a stricter budget and try to increase your income or reduce expenses."
    else:
        interpretation, reco = "[bold red]Warning! Your finances need immediate attention.[/bold red]", "Review your spending habits urgently. Focus on essential spending only."
    
    score_bar = ProgressBar(total=100, completed=total_score, width=50)

    summary_text = (
        f"Score: [bold]{total_score:.0f}/100[/bold]\n{score_bar}\n\n"
        f"{interpretation}\n\n[bold]Recommendation:[/bold] {reco}"
    )
    console.print(Panel(summary_text, title="[bold]Your Financial Health Score[/bold]"))


def handle_analytics():
    """Main function for the analytics feature."""
    while True:
        console.print("\n[bold cyan]Financial Analytics (CLI)[/bold cyan]")
        choice = questionary.select(
            "What would you like to do?",
            choices=["Generate Monthly Report", "Spending Analysis", "Financial Health Score", "Back to Main Menu"]
        ).ask()

        if choice == "Generate Monthly Report":
            generate_monthly_report()
        elif choice == "Spending Analysis":
            spending_analysis()
        elif choice == "Financial Health Score":
            financial_health_score()
        elif choice == "Back to Main Menu" or choice is None:
            break