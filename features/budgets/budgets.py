import questionary
from rich.console import Console
from rich.table import Table
from rich.progress_bar import ProgressBar
from rich.panel import Panel
from datetime import datetime
from features.common.utils import load_budgets, get_spending_for_month

# Initialize Rich Console
console = Console()

# Budget categories from GEMINI.md
BUDGET_CATEGORIES = ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Health", "Other"]

# Database files
BUDGETS_FILE = "database/budgets.txt"


def set_budget():
    """Sets a monthly budget for a specific category."""
    console.print("\n[bold green]-- Set a Monthly Budget --[/bold green]")

    category = questionary.select(
        "Select a category to budget:",
        choices=BUDGET_CATEGORIES
    ).ask()

    if not category:
        console.print("[bold red]Category not selected. Aborting.[/bold red]")
        return

    while True:
        amount_str = questionary.text(f"Enter your monthly budget for {category} (e.g., 500.00):").ask()
        if not amount_str:
            console.print("[bold red]Amount cannot be empty. Aborting.[/bold red]")
            return
        try:
            amount_float = float(amount_str)
            if amount_float <= 0:
                console.print("[bold red]Budget amount must be positive.[/bold red]")
                continue
            amount_paisa = int(amount_float * 100)
            break
        except ValueError:
            console.print("[bold red]Invalid amount. Please enter a number.[/bold red]")

    # Read existing budgets
    try:
        with open(BUDGETS_FILE, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []

    # Update or add the new budget
    updated = False
    new_lines = []
    for line in lines:
        if line.strip():
            parts = line.strip().split(',')
            if parts[0] == category:
                new_lines.append(f"{category},{amount_paisa}\n")
                updated = True
            else:
                new_lines.append(line)

    if not updated:
        new_lines.append(f"{category},{amount_paisa}\n")

    # Write back to the file
    try:
        with open(BUDGETS_FILE, "w") as f:
            f.writelines(new_lines)
        console.print(f"\n[bold green]Success![/bold green] Budget for [bold]{category}[/bold] set to {amount_str}.")
    except IOError as e:
        console.print(f"[bold red]Error writing to file {BUDGETS_FILE}: {e}[/bold red]")

def view_budgets():
    """Displays a table of budgets, spending, and utilization."""
    console.print("\n[bold yellow]-- Monthly Budget Status --[/bold yellow]")
    
    budgets = load_budgets() # Using shared function
    current_month = datetime.now().strftime("%Y-%m")
    spending = get_spending_for_month(current_month) # Using shared function

    if not budgets:
        console.print("[bold]No budgets set. Use 'Set Budget' to create one.[/bold]")
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Category", style="cyan")
    table.add_column("Budget", justify="right")
    table.add_column("Spent", justify="right")
    table.add_column("Remaining", justify="right")
    table.add_column("Utilization %", width=20)
    table.add_column("Status")

    total_budget = 0
    total_spent = 0
    over_budget_categories = []

    all_categories = set(budgets.keys()) | set(spending.keys())

    for category in sorted(list(all_categories)):
        budget_amount = budgets.get(category, 0)
        spent_amount = spending.get(category, 0)
        remaining = budget_amount - spent_amount
        
        if budget_amount > 0:
            utilization = (spent_amount / budget_amount) * 100
        else:
            utilization = 0 if spent_amount == 0 else 100
        
        if budget_amount == 0 and spent_amount > 0:
            status, remaining_style = "[bold yellow]No Budget[/bold yellow]", "yellow"
        elif utilization > 100:
            status, remaining_style = "[bold red]OVER[/bold red]", "red"
            over_budget_categories.append(category)
        elif utilization >= 70:
            status, remaining_style = "[bold yellow]Warning[/bold yellow]", "yellow"
        else:
            status, remaining_style = "[green]OK[/green]", "green"
            
        progress = ProgressBar(total=100, completed=min(utilization, 100), width=15)

        table.add_row(
            category,
            f"{budget_amount:.2f}",
            f"{spent_amount:.2f}",
            f"[{remaining_style}]{remaining:.2f}[/{remaining_style}]",
            progress,
            status
        )
        total_budget += budget_amount
        total_spent += spent_amount

    console.print(table)
    
    total_remaining = total_budget - total_spent
    overall_utilization = (total_spent / total_budget) * 100 if total_budget > 0 else 0
    
    summary_text = (
        f"Total Monthly Budget: [bold green]{total_budget:.2f}[/bold green]\n"
        f"Total Monthly Spent:  [bold red]{total_spent:.2f}[/bold red]\n"
        f"Total Remaining:      [bold cyan]{total_remaining:.2f}[/bold cyan]\n"
        f"Overall Utilization:  [bold magenta]{overall_utilization:.1f}%[/bold magenta]\n\n"
    )

    if over_budget_categories:
        summary_text += "[bold red]Attention![/bold red] You are over budget in: " + ", ".join(over_budget_categories)
        summary_text += "\nRecommendation: Review your spending in these areas to stay on track."
    else:
        summary_text += "[bold green]Looking good![/bold green] You are within your overall budget."
        summary_text += "\nRecommendation: Keep up the great work and continue monitoring your spending."

    console.print(Panel.fit(summary_text, title="[bold]Budget Summary[/bold]"))


def handle_budgets():
    """Main function for the budget feature."""
    while True:
        console.print("\n[bold cyan]Budget Management[/bold cyan]")
        choice = questionary.select(
            "What would you like to do?",
            choices=["Set Budget", "View Budgets", "Back to Main Menu"]
        ).ask()

        if choice == "Set Budget":
            set_budget()
        elif choice == "View Budgets":
            view_budgets()
        elif choice == "Back to Main Menu" or choice is None:
            break
