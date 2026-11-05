import csv
import re
from collections import defaultdict

tenants = {}
with open("data/tenants.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f, delimiter=";"):
        tenants.setdefault(row["iban"], []).append(row)
        
        with open("data/umsaetze.txt", encoding="utf-8") as f:
            raw = f.read()

lines = []
for line in raw.splitlines():
    if line.startswith(":"):
        lines.append(line)
    elif lines:
        lines[-1] += line

transactions = []
for line in lines:
    if line.startswith(":61:"):
        date = line[4:10]
        month = f"20{date[:2]}-{date[2:4]}"
        m = re.search(r"([CD])R?([\d,]+)", line[10:])
        amount = float(m.group(2).replace(",", "."))
        if m.group(1) == "D":
            amount = -amount
        transactions.append({"month": month, "amount": amount, "iban": "", "text": ""})
    elif line.startswith(":86:") and transactions:
        fields = dict(re.findall(r"\?(\d\d)([^?]*)", line))
        transactions[-1]["iban"] = fields.get("31", "")
        transactions[-1]["text"] = fields.get("20", "")

print(len(transactions), "transactions")
received = defaultdict(float)
for t in transactions:
    if t["amount"] > 0 and t["iban"] in tenants:
        received[(t["iban"], t["month"])] += t["amount"]
        months = ["2026-09", "2026-10"]
for month in months:
    print(f"\n=== {month} ===")
    for iban, rows in tenants.items():
        expected = sum(float(r["expected"]) for r in rows)
        names = " + ".join(r["tenant"] for r in rows)
        got = received.get((iban, month), 0)
        if got == 0:
            print(f"MISSING    {names:25s} expected {expected:.0f}")
        elif abs(got - expected) <= 10:
            print(f"ok         {names:25s} {got:.0f}")
        elif got < expected:
            print(f"UNDERPAID  {names:25s} {got:.0f} of {expected:.0f}")
        else:
            print(f"OVERPAID   {names:25s} {got:.0f} of {expected:.0f} (+{got-expected:.0f})")