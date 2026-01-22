# FSRS Flashcard Application Guide

## What is FSRS?

**FSRS (Free Spaced Repetition Scheduler)** is a modern spaced repetition algorithm that optimizes your study schedule based on your actual performance. Unlike older algorithms (like Anki's SM-2), FSRS uses machine learning research to predict optimal review times.

## How It Works

### Core Concepts

1. **Stability**: How long you can remember a card
   - Higher = you remember it longer
   - Increases when you rate cards well
   - Decreases when you forget

2. **Difficulty**: How inherently hard a card is for you
   - Scale: 1 (easy) to 10 (hard)
   - Increases when you struggle
   - Personalized to your learning

3. **Card States**:
   - **New**: Never reviewed
   - **Learning**: Being learned (short intervals)
   - **Review**: Learned (longer intervals)
   - **Relearning**: Forgotten, needs relearning

### The Algorithm Flow

```
Add Card (State: New)
    ↓
First Review → Rating (1-4)
    ↓
State: Learning (short intervals: minutes to days)
    ↓
Multiple Good Reviews
    ↓
State: Review (long intervals: days to months)
    ↓
If forgotten (Rating: Again)
    ↓
State: Relearning (back to shorter intervals)
```

### Rating System

- **1 (Again)**: Didn't remember → very short interval
- **2 (Hard)**: Struggled → shorter interval
- **3 (Good)**: Knew it → standard interval
- **4 (Easy)**: Very easy → longest interval

## Using the Application

### Running It

```bash
cd /home/chris/git/flashcards
.venv/bin/python src/fsrs_flashcards/main.py
```

### Menu Options

1. **Study due cards**: Review flashcards that are due
2. **Add new flashcard**: Create a question-answer pair
3. **List all flashcards**: See all cards with their status
4. **Show statistics**: View learning progress
5. **Exit**: Close the app

### Study Session Flow

1. Question appears
2. Think about the answer
3. Press Enter to reveal
4. Rate yourself (1-4)
5. See next review time
6. Move to next card

## Code Structure

### Files

- `main.py`: Main application code
- `flashcards.json`: Data storage (auto-created)
- `demo.py`: Demonstration script

### Key Classes

**FlashcardManager**: Main class managing everything

- `add_flashcard()`: Create new cards
- `get_due_flashcards()`: Find cards to review
- `review_flashcard()`: Process a review (calls FSRS)
- `study_session()`: Interactive review loop
- `list_flashcards()`: Display all cards
- `show_statistics()`: Show learning stats

### FSRS Integration

The key interaction with FSRS happens in `review_flashcard()`:

```python
# This line is where FSRS calculates optimal next review time
card, review_log = self.scheduler.review_card(card, rating, review_time)
```

The scheduler considers:

- Current card stability and difficulty
- Your rating (1-4)
- Time since last review
- Card's state in learning process

Then returns:

- Updated card with new due date
- Review log with scheduling details

## Example Learning Path

### Day 1: New Card

- Add: "What is Python?" → "A programming language"
- State: New
- Due: Immediately

### First Review (Rating: Good)

- Next review: ~4 minutes
- State: Learning
- Stability: Low (0.4)

### Second Review (Rating: Good)

- Next review: ~1 day
- State: Learning
- Stability: Increasing

### Third Review (Rating: Good)

- Next review: ~3 days
- State: Review
- Stability: Higher

### Fourth Review (Rating: Easy)

- Next review: ~8 days
- State: Review
- Stability: Much higher

### If You Forget (Rating: Again)

- Next review: ~10 minutes
- State: Relearning
- Difficulty: Increased
- Back to shorter intervals

## Benefits of FSRS

1. **Efficient**: Shows cards right when you might forget
2. **Adaptive**: Adjusts to your actual performance
3. **Personalized**: Difficulty tracked per-card
4. **Research-based**: Uses modern learning science

## Tips for Effective Use

1. **Be honest with ratings**: Don't rate "Easy" if you struggled
2. **Review regularly**: Check for due cards daily
3. **Keep cards simple**: One concept per card
4. **Add context**: Include hints in answers if needed
5. **Trust the algorithm**: Even long intervals are by design

## Advanced: Understanding the Data

Your `flashcards.json` stores:

```json
{
  "question": "Card question",
  "answer": "Card answer",
  "card_state": {
    "stability": 2.5, // Memory strength
    "difficulty": 5.2, // Card hardness
    "due": "2026-01-25T...", // Next review time
    "state": 2 // State (0=New, 1=Learning, 2=Review, 3=Relearning)
    // ... more FSRS metadata
  },
  "reviews": [
    // History of all reviews
  ]
}
```

## Troubleshooting

**No cards showing up for review?**

- Check statistics to see card states
- New cards appear immediately
- Review cards show when due date passes

**Want to reset a card?**

- Delete from `flashcards.json` and re-add
- Or manually edit the state to New (state: 0)

**App not starting?**

- Ensure virtual environment is activated
- Check that `fsrs` and `rich` packages are installed

## Next Steps

Potential enhancements:

- Import cards from CSV
- Export learning statistics
- Add tags/categories
- Search functionality
- Mobile app version
- Sync across devices

Happy learning! 🎴
