import questionary
from rich.console import Console
from rich.table import Table
from datetime import datetime

# Initialize Rich Console
console = Console()

# Transaction categories from GEMINI.md
EXPENSE_CATEGORIES = ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Health", "Other"]
INCOME_CATEGORIES = ["Salary", "Freelance", "Business", "Investment", "Gift", "Other"]

# Database file
TRANSACTIONS_FILE = "database/transactions.txt"

def add_transaction():
    """Adds a new transaction (expense or income) to the database file."""
    console.print("\n[bold green]-- Add a New Transaction --[/bold green]")

    transaction_type = questionary.select(
        "Select transaction type:",
        choices=["Expense", "Income"]
    ).ask()

    if not transaction_type:
        console.print("[bold red]Transaction type not selected. Aborting.[/bold red]")
        return

    if transaction_type == "Expense":
        category = questionary.select("Select category:", choices=EXPENSE_CATEGORIES).ask()
    else: # Income
        category = questionary.select("Select category:", choices=INCOME_CATEGORIES).ask()

    if not category:
        console.print("[bold red]Category not selected. Aborting.[/bold red]")
        return

    while True:
        amount_str = questionary.text("Enter amount (e.g., 12.50):").ask()
        if not amount_str:
            console.print("[bold red]Amount cannot be empty. Aborting.[/bold red]")
            return
        try:
            amount_float = float(amount_str)
            if amount_float <= 0:
                console.print("[bold red]Amount must be positive.[/bold red]")
                continue
            amount_paisa = int(amount_float * 100)
            break
        except ValueError:
            console.print("[bold red]Invalid amount. Please enter a number.[/bold red]")

    description = questionary.text("Enter a short description:").ask()
    if not description:
        description = "No description"
    
    if ',' in description:
        console.print("[yellow]Warning: Commas in description are not allowed and have been removed.[/yellow]")
        description = description.replace(',', ' ')


    transaction_date = datetime.now().strftime("%Y-%m-%d")

    # Format: date,type,category,amount_paisa,description
    transaction_record = f"{transaction_date},{transaction_type},{category},{amount_paisa},{description}\n"

    try:
        with open(TRANSACTIONS_FILE, "a") as f:
            f.write(transaction_record)
        console.print(f"\n[bold green]Success![/bold green] Transaction added: {transaction_type} of {amount_str} in {category}.")
    except IOError as e:
        console.print(f"[bold red]Error writing to file {TRANSACTIONS_FILE}: {e}[/bold red]")


def view_transactions():
    """Reads and displays all transactions from the database file in a table."""
    console.print("\n[bold yellow]-- All Transactions --[/bold yellow]")
    try:
        with open(TRANSACTIONS_FILE, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        console.print("[bold red]No transactions found. The transaction file does not exist.[/bold red]")
        return
    except IOError as e:
        console.print(f"[bold red]Error reading file {TRANSACTIONS_FILE}: {e}[/bold red]")
        return

    if not lines:
        console.print("[bold]No transactions recorded yet.[/bold]")
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Date", style="dim")
    table.add_column("Type")
    table.add_column("Category")
    table.add_column("Amount", justify="right")
    table.add_column("Description")

    for line in lines:
        try:
            date, trans_type, category, amount_paisa, description = line.strip().split(',', 4)
            # Convert paisa back to a float for display
            amount_display = float(amount_paisa) / 100
            
            # Style income as green and expense as red
            style = "green" if trans_type == "Income" else "red"
            
            table.add_row(
                date,
                trans_type,
                category,
                f"{amount_display:.2f}",
                description,
                style=style
            )
        except ValueError:
            console.print(f"[dim red]Skipping malformed line: {line.strip()}[/dim red]")
            continue
            
    console.print(table)


def handle_transactions():
    """Main function for the transaction feature."""
    while True:
        console.print("\n[bold cyan]Transaction Management[/bold cyan]")
        choice = questionary.select(
            "What would you like to do?",
            choices=["Add Transaction", "View Transactions", "Back to Main Menu"]
        ).ask()

        if choice == "Add Transaction":
            add_transaction()
        elif choice == "View Transactions":
            view_transactions()
        elif choice == "Back to Main Menu" or choice is None:
            break
