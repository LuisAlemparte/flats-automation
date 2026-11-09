import csv
import os
from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic()

CATEGORIES = ["repair", "payment", "question", "other"]

PROMPT = """Du bist Assistent einer Hausverwaltung. Ordne die folgende Mieter-E-Mail
genau einer Kategorie zu: repair, payment, question, other.
Antworte nur mit dem einen Wort.

E-Mail:
{text}"""


def classify(text):
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=5,
        messages=[{"role": "user", "content": PROMPT.format(text=text)}],
    )
    answer = response.content[0].text.strip().lower()
    return answer if answer in CATEGORIES else "other"


correct = 0
rows = list(csv.DictReader(open("data/emails_labelled.csv", encoding="utf-8"), delimiter=";"))
for row in rows:
    predicted = classify(row["text"])
    hit = predicted == row["category"]
    correct += hit
    mark = "ok " if hit else "XX "
    print(f"{mark} {row['id']:>3}  expected {row['category']:9s} got {predicted:9s} {row['text'][:50]}")

print(f"\nAccuracy: {correct}/{len(rows)} = {correct / len(rows):.0%}")
