import csv
import os
import sys
from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic()

CATEGORIES = ["repair", "payment", "question", "other"]

PROMPT = """Du bist Assistent einer Hausverwaltung. Ordne die folgende Mieter-E-Mail
genau einer Kategorie zu:
- repair: etwas in der Wohnung oder im Haus ist defekt, verschmutzt oder stört und der Vermieter muss handeln
- payment: es geht um die Mietzahlung des Mieters (überwiesen, verspätet, zu viel/zu wenig, Teilzahlung, neues Konto), auch wenn es als Frage formuliert ist
- question: der Mieter fragt etwas oder bittet um eine Entscheidung oder Erklärung (Kündigung, Nachbarn, Erlaubnis, Termine, Abrechnung)
- other: reine Information ohne Handlungsbedarf (Danke, Urlaub, Dokument anbei)
Wenn mehrere passen, nimm die, bei der der Vermieter handeln muss.
Antworte nur mit dem einen Wort.

E-Mail:
{text}"""
REPLY_SYSTEM = """Du bist der Vermieter zweier Mehrfamilienhäuser in Karlsruhe-Durlach und antwortest auf E-Mails deiner Mieter.
Haltung: erfahren, korrekt, respektvoll, aber bestimmt. Du kennst das deutsche Mietrecht und den Mietvertrag.
Du bleibst freundlich, lässt dich aber nicht unter Druck setzen und machst keine Zusagen, die du nicht halten kannst.
Regeln:
- Antworte auf Deutsch, Sie-Form, kurz (max. 120 Wörter), kein Smalltalk.
- Bei Reparaturen: bestätige den Eingang, nenne den nächsten konkreten Schritt und bis wann.
- Bei Zahlungsfragen: nenne den vertraglichen Stand, dann die Lösung.
- Bei Fragen: beantworte sie klar; wenn du etwas prüfen musst, sage das und nenne einen Termin.
- Wenn der Mieter droht (Mietminderung, Anwalt): bleib ruhig, verweise auf den Vertrag, keine Rechtfertigung.
- Unterschrift: "Mit freundlichen Grüßen, Weingärtner"
"""


def classify(text):
    response = client.messages.create(
        model="claude-haiku-5-5",
        max_tokens=1000,
        messages=[{"role": "user", "content": PROMPT.format(text=text)}],
    )
    answer = "".join(b.text for b in response.content if b.type == "text").strip().lower()
    if answer not in CATEGORIES:
        print(f"    [unexpected answer: {answer!r}]")
        return "other"
    return answer
    

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
    seen = {row["text"] for row in existing}

    with open(tickets_path, "a", encoding="utf-8", newline="") as out:
        writer = csv.writer(out, delimiter=";")
        if not existing:
            writer.writerow(["id", "date", "tenant", "category", "status", "text"])
        for row in csv.DictReader(open("data/inbox.csv", encoding="utf-8"), delimiter=";"):
            if row["text"] in seen:
                continue
            category = classify(row["text"])
            writer.writerow([next_id, row["date"], row["tenant"], category, "open", row["text"]])
            print(f"#{next_id}  {row['date']}  {row['tenant']:12s} {category:9s} {row['text'][:50]}")
            next_id += 1

def close_ticket(ticket_id):
    tickets_path = "data/tickets.csv"
    rows = list(csv.DictReader(open(tickets_path, encoding="utf-8"), delimiter=";"))
    found = False
    for row in rows:
        if row["id"] == ticket_id:
            row["status"] = "done"
            found = True
    if not found:
        print(f"No ticket with id {ticket_id}")
        return
    with open(tickets_path, "w", encoding="utf-8", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=rows[0].keys(), delimiter=";")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Ticket {ticket_id} closed")

def draft_reply(ticket_id):
    rows = list(csv.DictReader(open("data/tickets.csv", encoding="utf-8"), delimiter=";"))
    ticket = next((r for r in rows if r["id"] == ticket_id), None)
    if ticket is None:
        print(f"No ticket with id {ticket_id}")
        return
    response = client.messages.create(
        model="claude-sonnet-5-5",
        max_tokens=2000,
        system=REPLY_SYSTEM,
        messages=[{"role": "user", "content": f"E-Mail von Mieter {ticket['tenant']} ({ticket['category']}):\n\n{ticket['text']}\n\nSchreibe die Antwort."}],
    )
    print(f"--- Entwurf für Ticket #{ticket_id} ({ticket['tenant']}) ---\n")
    text = "".join(block.text for block in response.content if block.type == "text")
    print(text)
    os.makedirs("output/antworten", exist_ok=True)
    with open(f"output/antworten/ticket-{ticket_id}.md", "w", encoding="utf-8") as f:
        f.write(f"# Ticket #{ticket_id} – {ticket['tenant']} ({ticket['category']})\n\n")
        f.write(f"## Mieter schrieb\n\n{ticket['text']}\n\n## Entwurf\n\n{text}\n")


if len(sys.argv) > 1 and sys.argv[1] == "inbox":
    process_inbox()
elif len(sys.argv) > 2 and sys.argv[1] == "close":
    close_ticket(sys.argv[2])
elif len(sys.argv) > 2 and sys.argv[1] == "reply":
    draft_reply(sys.argv[2])
else:
    evaluate()
