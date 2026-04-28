"""
Example: Importing flashcards from CSV file.
This shows how to extend the flashcard app with new features.
"""

import csv
import sys
from pathlib import Path

repo_root = Path(__file__).parent.parent.parent
sys.path.append(str(repo_root))

from InquirerPy import inquirer
from rich.console import Console
from rich.prompt import Prompt

from src.fsrs_flashcards.main import FlashcardManager, select_flashcard_file

console = Console()


def import_from_csv(csv_file: str, manager: FlashcardManager):
    """
    Import flashcards from a CSV file with 'question' and 'answer' columns.
    Supports both comma (,) and semicolon (;) delimiters - auto-detects.

    CSV format:
    question,answer  OR  question;answer
    "What is Python?","A programming language"
    "What is FSRS?","Free Spaced Repetition Scheduler"
    """
    csv_path = Path(csv_file)

    if not csv_path.exists():
        console.print(f"[red]Error: File {csv_file} not found[/red]")
        return

    imported = 0

    with open(csv_path, "r", encoding="utf-8") as f:
        # Auto-detect delimiter (comma or semicolon)
        sample = f.read(1024)
        f.seek(0)
        sniffer = csv.Sniffer()
        try:
            delimiter = sniffer.sniff(sample).delimiter
        except csv.Error:
            # Default to comma if detection fails
            delimiter = ","

        reader = csv.DictReader(f, delimiter=delimiter)

        for row in reader:
            question = row.get("question", "").strip()
            answer = row.get("answer", "").strip()

            if question and answer:
                manager.add_flashcard(question, answer)
                imported += 1

    console.print(f"[green]✓ Imported {imported} flashcards from {csv_file}[/green]")


def export_to_csv(csv_file: str, manager: FlashcardManager, delimiter: str = ","):
    """
    Export flashcards to a CSV file.
    Useful for backup or editing in spreadsheet software.

    Args:
        csv_file: Path to output file
        manager: FlashcardManager instance
        delimiter: ',' for comma or ';' for semicolon (default: ',')
    """
    csv_path = Path(csv_file)

    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["question", "answer", "reviews", "state"],
            delimiter=delimiter,
        )
        writer.writeheader()

        for fc in manager.flashcards:
            writer.writerow(
                {
                    "question": fc["question"],
                    "answer": fc["answer"],
                    "reviews": len(fc["reviews"]),
                    "state": fc["card_state"].get("state", 0),
                }
            )

    delim_name = "semicolon" if delimiter == ";" else "comma"
    console.print(
        f"[green]✓ Exported {len(manager.flashcards)} flashcards to {csv_file} ({delim_name}-delimited)[/green]"
    )


def create_sample_csv(delimiter: str = ","):
    """Create a sample CSV file with example flashcards.

    Args:
        delimiter: ',' for comma or ';' for semicolon (default: ',')
    """
    sample_data = [
        ("What is the speed of light?", "299,792,458 meters per second"),
        ("Who wrote 'Romeo and Juliet'?", "William Shakespeare"),
        ("What is the chemical symbol for gold?", "Au"),
        ("What year did World War II end?", "1945"),
        ("What is the largest planet in our solar system?", "Jupiter"),
        ("What is the capital of Japan?", "Tokyo"),
        ("What is the square root of 144?", "12"),
        ("Who painted the Mona Lisa?", "Leonardo da Vinci"),
        ("What is the boiling point of water?", "100°C or 212°F"),
        ("What is the smallest prime number?", "2"),
    ]

    with open("sample_flashcards.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter=delimiter)
        writer.writerow(["question", "answer"])
        writer.writerows(sample_data)

    delim_name = "semicolon" if delimiter == ";" else "comma"
    console.print(
        f"[green]✓ Created sample_flashcards.csv with 10 example cards ({delim_name}-delimited)[/green]"
    )


if __name__ == "__main__":
    console.print("[bold cyan]CSV Import/Export Tool[/bold cyan]\n")

    # Let user select which flashcard file to work with
    data_file = select_flashcard_file()
    if data_file is None:
        console.print("\n[yellow]No file selected. Exiting.[/yellow]\n")
        raise SystemExit(0)
    manager = FlashcardManager(data_file)

    while True:
        console.print()
        choice = inquirer.select(
            message="What would you like to do?",
            choices=[
                {"name": "📝 Create sample CSV file", "value": "create"},
                {"name": "📥 Import flashcards from CSV", "value": "import"},
                {"name": "📤 Export flashcards to CSV", "value": "export"},
                {"name": "🔄 Switch flashcard file", "value": "switch"},
                {"name": "🚪 Exit", "value": "exit"},
            ],
        ).execute()

        if choice == "create":
            delimiter = inquirer.select(
                message="Select delimiter:",
                choices=[
                    {"name": "Comma (,)", "value": ","},
                    {"name": "Semicolon (;)", "value": ";"},
                ],
                default=",",
            ).execute()
            console.print("\n[bold]Creating sample CSV...[/bold]")
            create_sample_csv(delimiter)
            console.print()

        elif choice == "import":
            filename = Prompt.ask(
                "\n[cyan]CSV file to import from[/cyan]",
                default="sample_flashcards.csv",
            )
            console.print(f"\n[bold]Importing from {filename}...[/bold]")
            import_from_csv(filename, manager)
            console.print()

        elif choice == "export":
            if not manager.flashcards:
                console.print(
                    "\n[yellow]No flashcards to export. Import or add some first![/yellow]\n"
                )
            else:
                filename = Prompt.ask(
                    "\n[green]CSV file to export to[/green]",
                    default="flashcards_backup.csv",
                )
                delimiter = inquirer.select(
                    message="Select delimiter:",
                    choices=[
                        {"name": "Comma (,)", "value": ","},
                        {"name": "Semicolon (;)", "value": ";"},
                    ],
                    default=",",
                ).execute()
                console.print(f"\n[bold]Exporting to {filename}...[/bold]")
                export_to_csv(filename, manager, delimiter)
                console.print()

        elif choice == "switch":
            console.print("\n[bold cyan]Switching flashcard file...[/bold cyan]")
            data_file = select_flashcard_file()
            if data_file is not None:
                manager = FlashcardManager(data_file)
            else:
                console.print("[yellow]Keeping current flashcard file.[/yellow]")

        elif choice == "exit":
            console.print("\n[cyan]Done! 📁[/cyan]\n")
            break
