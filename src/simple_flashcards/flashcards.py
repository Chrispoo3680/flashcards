import random

import pandas as pd
from rich import print

df = pd.read_csv("flashcards.csv", delimiter=";")

words = df["ord"]
meanings = df["betydning"]


class flashcard:
    def __init__(self, word: str, meaning: str):
        self.word = word.replace("(uttr.)", "").replace("/ue/", "").replace("/ie/", "")
        self.meaning = (
            meaning.replace("(uttr.)", "").replace("/ue/", "").replace("/ie/", "")
        )


cards = [flashcard(words[n], meanings[n]) for n in range(len(words))]
random.shuffle(cards)

score = 0

for i, c in enumerate(cards):
    print(f"\n>  {c.meaning}")
    inp = input("-  ")
    if inp.replace(" ", "") == c.word.split(",")[0].replace(" ", "") and inp:
        print(f"[green]=  {c.word}\t\t\t\t\t[purple]({i+1})")
        score += 1
    else:
        print(f"[red]x  {c.word}\t\t\t\t\t[purple]({i+1})")

print(f"\n\nYou got {score}/{len(cards)} right answers.\n")
