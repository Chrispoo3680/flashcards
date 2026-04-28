# flashcards

Flashcard scripts for remembering new information. Uses techniques like spaced repetition.

**Overview**

This project contains a terminal-based flashcard program you can use to practice and remember facts. The interactive app uses the FSRS spaced-repetition algorithm to schedule reviews.

This README explains, step-by-step, how to set up and run the applications. The instructions are written for people who are not programmers and assume you can copy-and-paste commands into a terminal.

**What you'll need**

- A computer (Windows, macOS or Linux)
- Python 3.13 or newer (the project requires at least Python 3.13)
- A terminal or command prompt (Terminal on macOS, Command Prompt or PowerShell on Windows, Terminal on Linux)

If you don't already have Python, see python.org for downloads or use your system's app store or package manager.

---

**Quick start (Linux / macOS / Windows PowerShell)**

1. Open a terminal (or PowerShell on Windows).
2. Change to the project folder. For example, if you put the project in a folder called `flashcards` in your home folder, run:

```bash
cd ~/flashcards
```

3. (Optional, but recommended) Upgrade pip and create an isolated environment:

```bash
python -m pip install --upgrade pip
python -m venv .venv
# Activate the environment:
# On macOS / Linux:
source .venv/bin/activate
# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1
```

4. Install the required packages (these make the app work). Copy and paste this single command into your terminal:

```bash
python -m pip install fsrs inquirerpy ipykernel matplotlib numpy pandas rich
```

5. Run the main FSRS-based flashcard app (interactive menu):

```bash
python src/fsrs_flashcards/main.py
```

---

**Using the FSRS interactive app**

After starting the FSRS app with `python src/fsrs_flashcards/main.py`, you will see a small text menu. Use your keyboard (arrow keys and Enter) to choose an option. The main options are:

- `Study due cards`: Runs a study session for cards that are due for review. You'll see a question, type an answer (or press Enter to skip), then rate how well you knew it.
- `Add new flashcard`: Type a question and an answer to add a card to the current dataset.
- `List all flashcards`: Shows the cards you have saved and their status.
- `Show statistics`: Displays simple learning statistics.
- `Change flashcard file`: Choose a different file to store/load cards. This is useful if you want separate decks (for example `film_vocab.json` or `history_vocab.json`).
- `Exit`: Close the program.

How cards are stored:

- Flashcards are saved in the `data/` folder as JSON files (e.g. `data/flashcards.json`). When you first run the app it will let you create a new file or pick an existing one from `data/`.
- You do not need to edit files by hand. Use the app's `Add new flashcard` menu to create cards.

Reviewing flow:

1. The app shows the question.
2. Type your answer (or press Enter to skip).
3. The app displays the correct answer and asks you to rate how well you knew it (1-4). Your rating updates the card's next review time automatically.

---

**Importing new flashcards from CSV (bulk add)**

If you have many new cards, you can import them from a CSV file using the included CSV import tool.

**Step 1: Create a CSV file**

The CSV file must have exactly two columns with this header row:

```text
question,answer
```

Each new card goes on its own line. Use quotes around text, especially if it contains commas.

Example:

```text
question,answer
"What is the capital of Japan?","Tokyo"
"What is the chemical symbol for gold?","Au"
```

The importer accepts both comma `,` and semicolon `;` separators. If you use semicolons, the header should be:

```text
question;answer
```

**Step 2: Place the CSV file in the project folder**

Save the file anywhere inside the project (the main folder). For example: `my_cards.csv`.

**Step 3: Run the CSV import tool**

```bash
python src/fsrs_flashcards/csv_importer.py
```

**Step 4: Import your cards**

1. Choose which flashcard deck (JSON file) to import into.
2. Select `Import flashcards from CSV` from the menu.
3. Type the CSV filename (for example `my_cards.csv`) and press Enter.

Tip: The menu also has `Create sample CSV file`, which generates a ready-to-edit example CSV so you can copy the format.

---

**Prompting an LLM to generate a correct CSV file**

If you have a messy list of new flashcards (notes, bullet points, or "question - answer" lines), you can ask an LLM (like ChatGPT or Copilot) to convert it into a CSV file.

Use a prompt like this (copy and paste, then add your list at the end):

```text
You are a data formatter. Convert the following flashcards into a CSV file.
Rules:
- Output ONLY the CSV text. No explanations.
- Use a comma delimiter.
- Include a header row: question,answer
- One flashcard per line.
- Quote every field with double quotes.
- If a field contains a double quote, escape it by doubling it ("").

Here is the raw list to convert:
<PASTE YOUR LIST HERE>
```

After you get the CSV output, copy it into a new file (for example `my_cards.csv`) and import it using the steps above.

If you want the LLM to pick questions and answers from mixed notes, add a line like:

```text
If a line looks like "Question - Answer", split at the dash. If it is a single fact, turn it into a "What is/Who is" question.
```

Always scan the CSV for mistakes before importing, especially if the original notes were messy.

---

**Where your data lives**

- The `data/` folder in the project contains some example CSV and JSON files such as `spanish_verbs.csv` and `spanish_verbs.json`. You can choose these files from the FSRS app's file selection menu, or create new JSON files from the app.
- JSON files created by the app contain the saved flashcards and the scheduling data used by FSRS.

---

**Basic troubleshooting**

- "Command not found" when running `python`: Try `python3` instead of `python` (some systems use `python3` for recent Python versions).
- If package installation fails, copy the error shown in the terminal and search for it online or ask for help. Common fixes:
  - Use `python -m pip install --user ...` to install packages for your user only.
  - Ensure you are using Python 3.13 or newer.
- If the FSRS app shows no files in the `data/` folder, pick `Create new file` and give it a name like `my_deck.json`.

---

**If you need help**

- If you are stuck, tell a helper the exact error message and what command you ran (copy-paste). That makes troubleshooting much faster.

---

**Developer notes (for maintainers)**

- The project lists these Python dependencies in `pyproject.toml`: `fsrs`, `inquirerpy`, `ipykernel`, `matplotlib`, `numpy`, `pandas`, `rich`.
- Entry points used for interactive use are the scripts under `src/`:
  - `src/fsrs_flashcards/main.py` — full FSRS-based TUI app.
