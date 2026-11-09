import csv
import os
import sys
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

def evaluate():
    correct = 0
    rows = list(csv.DictReader(open("data/emails_labelled.csv", encoding="utf-8"), delimiter=";"))
    for row in rows:
        predicted = classify(row["text"])
        hit = predicted == row["category"]
        correct += hit
        mark = "ok " if hit else "XX "
        print(f"{mark} {row['id']:>3}  expected {row['category']:9s} got {predicted:9s} {row['text'][:50]}")
    print(f"\nAccuracy: {correct}/{len(rows)} = {correct / len(rows):.0%}")

def process_inbox():
    tickets_path = "data/tickets.csv"
    existing = []
    if os.path.exists(tickets_path):
        existing = list(csv.DictReader(open(tickets_path, encoding="utf-8"), delimiter=";"))
    next_id = len(existing) + 1

    with open(tickets_path, "a", encoding="utf-8", newline="") as out:
        writer = csv.writer(out, delimiter=";")
        if not existing:
            writer.writerow(["id", "date", "tenant", "category", "status", "text"])
        for row in csv.DictReader(open("data/inbox.csv", encoding="utf-8"), delimiter=";"):
            category = classify(row["text"])
            writer.writerow([next_id, row["date"], row["tenant"], category, "open", row["text"]])
            print(f"#{next_id}  {row['date']}  {row['tenant']:12s} {category:9s} {row['text'][:50]}")
            next_id += 1

if len(sys.argv) > 1 and sys.argv[1] == "inbox":
    process_inbox()
else:
    evaluate()
