"""
Terminal-based flashcard application using FSRS algorithm.
FSRS adapts review intervals based on your performance, optimizing learning.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from fsrs import Card, Rating, Scheduler, State
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

# Initialize console for pretty output
console = Console()

# Data file to store flashcards
DATA_FILE = Path(__file__).parent.parent.parent / "data/flashcards.json"


class FlashcardManager:
    """Manages flashcards with FSRS scheduling."""

    def __init__(self):
        self.scheduler = Scheduler()
        self.flashcards: List[Dict] = []
        self.load_flashcards()

    def load_flashcards(self):
        """Load flashcards from JSON file."""
        if DATA_FILE.exists():
            with open(DATA_FILE, "r") as f:
                self.flashcards = json.load(f)
        else:
            self.flashcards = []

    def save_flashcards(self):
        """Save flashcards to JSON file."""
        with open(DATA_FILE, "w") as f:
            json.dump(self.flashcards, f, indent=2)

    def add_flashcard(self, question: str, answer: str):
        """Add a new flashcard with initial FSRS state."""
        # Create a new Card object - this initializes FSRS tracking
        card = Card()

        flashcard = {
            "question": question,
            "answer": answer,
            "card_state": self._card_to_dict(
                card
            ),  # Store FSRS card state (properly serialized)
            "created_at": datetime.now(timezone.utc).isoformat(),
            "reviews": [],  # History of reviews
        }

        self.flashcards.append(flashcard)
        self.save_flashcards()
        console.print(f"[green]✓[/green] Added flashcard: {question}")

    def get_due_flashcards(self) -> List[Dict]:
        """Get flashcards that are due for review."""
        now = datetime.now(timezone.utc)
        due_cards = []

        for fc in self.flashcards:
            card = self._dict_to_card(fc["card_state"])
            # New cards (state=0) or cards past their due date
            if card.state == 0 or card.due <= now:
                due_cards.append(fc)

        return due_cards

    def _dict_to_card(self, card_dict: Dict) -> Card:
        """Convert dictionary back to Card object."""
        card = Card()
        for key, value in card_dict.items():
            if key == "due" and value:
                # Convert ISO string back to datetime
                setattr(card, key, datetime.fromisoformat(value))
            elif key == "last_review" and value:
                setattr(card, key, datetime.fromisoformat(value))
            elif key == "state":
                # Convert state integer to State enum
                setattr(card, key, State(value))
            else:
                setattr(card, key, value)
        return card

    def _card_to_dict(self, card: Card) -> Dict:
        """Convert Card object to dictionary for JSON storage."""
        card_dict = card.__dict__.copy()
        # Convert datetime to ISO string for JSON
        if card_dict.get("due"):
            card_dict["due"] = card_dict["due"].isoformat()
        if card_dict.get("last_review"):
            card_dict["last_review"] = card_dict["last_review"].isoformat()
        # Convert State enum to integer
        if isinstance(card_dict.get("state"), State):
            card_dict["state"] = card_dict["state"].value
        return card_dict

    def review_flashcard(self, flashcard: Dict, rating: Rating):
        """Review a flashcard and update its FSRS state."""
        # Convert stored state back to Card object
        card = self._dict_to_card(flashcard["card_state"])

        # Get review time
        review_time = datetime.now(timezone.utc)

        # Schedule next review based on rating
        # This is where FSRS magic happens - it calculates optimal next review time
        card, review_log = self.scheduler.review_card(card, rating, review_time)

        # Update flashcard with new card state
        flashcard["card_state"] = self._card_to_dict(card)

        # Store review in history
        flashcard["reviews"].append(
            {
                "rating": rating.value,
                "reviewed_at": review_log.review_datetime.isoformat(),
                "state": card.state.value,
                "due": card.due.isoformat() if card.due else None,
            }
        )

        self.save_flashcards()
        return card, review_log

    def study_session(self):
        """Run an interactive study session."""
        due_cards = self.get_due_flashcards()

        if not due_cards:
            console.print("[yellow]No cards due for review! Great job! 🎉[/yellow]")
            return

        console.print(
            f"\n[cyan]Starting study session with {len(due_cards)} cards[/cyan]\n"
        )

        for idx, flashcard in enumerate(due_cards, 1):
            # Display question
            console.print(
                Panel(
                    f"[bold]{flashcard['question']}[/bold]",
                    title=f"Card {idx}/{len(due_cards)}",
                    border_style="cyan",
                )
            )

            # Ask user to type their answer
            user_answer = (
                Prompt.ask("\n[cyan]Your answer[/cyan] (or press Enter to skip)") or ""
            )

            # Show correct answer
            console.print(
                Panel(
                    f"[green]{flashcard['answer']}[/green]",
                    title="Correct Answer",
                    border_style="green",
                )
            )

            # Show comparison if user provided an answer
            if user_answer.strip():
                correct_answer = flashcard["answer"].strip()
                user_answer_clean = user_answer.strip()

                if user_answer_clean.lower() == correct_answer.lower():
                    console.print("\n[bold green]✓ Exact match![/bold green]")
                else:
                    console.print("\n[bold yellow]✗ Different answer[/bold yellow]")
                    console.print(f"  You wrote: [cyan]{user_answer_clean}[/cyan]")
                    console.print(f"  Expected:  [green]{correct_answer}[/green]")

            console.print()

            # Get rating from user
            console.print("\nHow well did you know this?")
            console.print("  [red]1[/red] - Again (didn't know)")
            console.print("  [yellow]2[/yellow] - Hard (struggled)")
            console.print("  [green]3[/green] - Good (knew it)")
            console.print("  [cyan]4[/cyan] - Easy (very easy)")

            while True:
                rating_str = Prompt.ask("Your rating", choices=["1", "2", "3", "4"])
                rating = Rating(int(rating_str))
                break

            # Update card with FSRS
            card, review_log = self.review_flashcard(flashcard, rating)

            # Show scheduling info
            if card.due:
                now = datetime.now(timezone.utc)
                time_diff = card.due - now
                total_seconds = time_diff.total_seconds()

                if total_seconds < 60:
                    time_str = "less than a minute"
                elif total_seconds < 3600:  # Less than 1 hour
                    minutes = int(total_seconds / 60)
                    time_str = f"{minutes} minute{'s' if minutes != 1 else ''}"
                elif total_seconds < 86400:  # Less than 1 day
                    hours = int(total_seconds / 3600)
                    minutes = int((total_seconds % 3600) / 60)
                    time_str = f"{hours} hour{'s' if hours != 1 else ''}"
                    if minutes > 0:
                        time_str += f", {minutes} minute{'s' if minutes != 1 else ''}"
                else:  # 1 day or more
                    days = int(total_seconds / 86400)
                    remaining_seconds = total_seconds % 86400
                    hours = int(remaining_seconds / 3600)
                    time_str = f"{days} day{'s' if days != 1 else ''}"
                    if hours > 0:
                        time_str += f", {hours} hour{'s' if hours != 1 else ''}"

                console.print(f"\n[dim]Next review in {time_str}[/dim]")
            else:
                console.print("\n[dim]Next review: Not scheduled[/dim]")
            state_name = "New" if card.state == 0 else State(card.state).name
            console.print(f"[dim]Card state: {state_name}[/dim]\n")
            console.print("─" * 60 + "\n")

    def list_flashcards(self):
        """Display all flashcards with their review status."""
        if not self.flashcards:
            console.print("[yellow]No flashcards yet. Add some first![/yellow]")
            return

        table = Table(title="Your Flashcards")
        table.add_column("#", justify="right", style="cyan")
        table.add_column("Question", style="white")
        table.add_column("State", justify="center")
        table.add_column("Reviews", justify="center", style="yellow")
        table.add_column("Next Due", style="green")

        now = datetime.now(timezone.utc)

        for idx, fc in enumerate(self.flashcards, 1):
            card = self._dict_to_card(fc["card_state"])
            state_name = "New" if card.state == 0 else State(card.state).name
            review_count = len(fc["reviews"])

            # Format due date
            if card.due:
                time_diff = card.due - now
                if time_diff.total_seconds() < 0:
                    due_str = "[red]OVERDUE[/red]"
                elif time_diff.total_seconds() < 3600:
                    due_str = "Now"
                elif time_diff.days < 1:
                    hours = time_diff.seconds // 3600
                    due_str = f"In {hours}h"
                else:
                    due_str = f"In {time_diff.days}d"
            else:
                due_str = "New"

            table.add_row(
                str(idx),
                (
                    fc["question"][:50] + "..."
                    if len(fc["question"]) > 50
                    else fc["question"]
                ),
                state_name,
                str(review_count),
                due_str,
            )

        console.print(table)

    def show_statistics(self):
        """Display learning statistics."""
        if not self.flashcards:
            console.print(
                "[yellow]No statistics yet. Add and review some flashcards first![/yellow]"
            )
            return

        total = len(self.flashcards)
        due = len(self.get_due_flashcards())

        state_counts = {
            0: 0,  # New
            State.Learning: 0,
            State.Review: 0,
            State.Relearning: 0,
        }
        total_reviews = 0

        for fc in self.flashcards:
            card = self._dict_to_card(fc["card_state"])
            state_counts[card.state] = state_counts.get(card.state, 0) + 1
            total_reviews += len(fc["reviews"])

        console.print("\n[bold cyan]📊 Learning Statistics[/bold cyan]")
        console.print(f"  Total cards: {total}")
        console.print(f"  Due for review: {due}")
        console.print(f"  Total reviews: {total_reviews}")
        console.print("\n[bold]Card States:[/bold]")
        console.print(f"  New: {state_counts[0]}")
        console.print(f"  Learning: {state_counts[State.Learning]}")
        console.print(f"  Review: {state_counts[State.Review]}")
        console.print(f"  Relearning: {state_counts[State.Relearning]}\n")


def main():
    """Main application loop."""
    manager = FlashcardManager()

    console.print("\n[bold cyan]🎴 FSRS Flashcard App[/bold cyan]")
    console.print("[dim]Spaced repetition that adapts to your learning[/dim]\n")

    while True:
        console.print("[bold]What would you like to do?[/bold]")
        console.print("  1. Study due cards")
        console.print("  2. Add new flashcard")
        console.print("  3. List all flashcards")
        console.print("  4. Show statistics")
        console.print("  5. Exit")

        choice = Prompt.ask("\nChoice", choices=["1", "2", "3", "4", "5"])

        if choice == "1":
            manager.study_session()

        elif choice == "2":
            question = Prompt.ask("\n[cyan]Question[/cyan]")
            answer = Prompt.ask("[green]Answer[/green]")
            manager.add_flashcard(question, answer)
            console.print()

        elif choice == "3":
            console.print()
            manager.list_flashcards()
            console.print()

        elif choice == "4":
            manager.show_statistics()

        elif choice == "5":
            console.print("\n[cyan]Happy learning! 📚[/cyan]\n")
            break


if __name__ == "__main__":
    main()
