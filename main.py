import questionary
from rich.console import Console
import subprocess
import sys
from features.transactions.transactions import handle_transactions
from features.budgets.budgets import handle_budgets
from features.analytics.analytics import handle_analytics

console = Console()

def launch_dashboard():
    """Launches the Streamlit web dashboard."""
    console.print("\n[bold yellow]Launching the web dashboard...[/bold yellow]")
    console.print("You can view it in your web browser.")
    console.print("Press [bold]Ctrl+C[/bold] in this terminal to stop the dashboard.")
    try:
        process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "dashboard.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            console.print("[bold red]Error launching dashboard:[/bold red]")
            console.print(stderr.decode())
    except FileNotFoundError:
        console.print("[bold red]Error: 'streamlit' is not installed.[/bold red]")
        console.print("Please run 'pip install streamlit' to use the web dashboard.")
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred: {e}[/bold red]")


def main_menu():
    while True:
        choice = questionary.select(
            "What do you want to do?",
            choices=[
                "Transaction Management",
                "Budgeting",
                "Financial Analytics (CLI)",
                "Launch Web Dashboard",
                "Exit"
            ]
        ).ask()

        if choice == "Transaction Management":
            handle_transactions()
        elif choice == "Budgeting":
            handle_budgets()
        elif choice == "Financial Analytics (CLI)":
            handle_analytics()
        elif choice == "Launch Web Dashboard":
            launch_dashboard()
        elif choice == "Exit" or choice is None:
            console.print("[bold red]Exiting the application. Goodbye![/bold red]")
            break

def main():
    console.print("[bold cyan]Welcome to Personal Finance Tracker CLI![/bold cyan]")
    main_menu()

if __name__ == "__main__":
    main()