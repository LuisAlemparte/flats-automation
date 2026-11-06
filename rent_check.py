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
        year = int("20" + date[:2])
        mon = int(date[2:4])
        day = int(date[4:6])
        if day >= 29:
            mon += 1
            if mon == 13:
                mon = 1 
                year += 1
        month = f"{year}-{mon:02d}"
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

# Sort each tenant transfer into rent or other
received = defaultdict(float)
other = defaultdict(list)
for t in transactions:
    if t["amount"] <= 0 or t["iban"] not in tenants:
        continue
    expected_any = [float(r["expected"]) for r in tenants[t["iban"]]]
    is_rent = "miete" in t["text"].lower() or any(abs(t["amount"] - e) <= 10 for e in expected_any)
    if is_rent:
        received[(t["iban"], t["month"])] += t["amount"]
    else:
        other[t["month"]].append((t["iban"], t["amount"], t["text"][:50]))

# Compare per month, per tenant
months = ["2026-09", "2026-10"]
for month in months:
    print(f"\n=== {month} ===")
    for iban, rows in tenants.items():
        active = {}
        for r in rows:
            if r["valid_from"][:7] <= month:
                active[r["flat"]] = r
        active = list(active.values())
        if not active:
            continue
        expected = sum(float(r["expected"]) for r in active)
        names = " + ".join(r["tenant"] for r in active)
        got = received.get((iban, month), 0)
        if got == 0:
            print(f"MISSING    {names:25s} expected {expected:.0f}")
        elif abs(got - expected) <= 10:
            print(f"ok         {names:25s} {got:.0f}")
        elif got < expected:
            print(f"UNDERPAID  {names:25s} {got:.0f} of {expected:.0f}")
        else:
            print(f"OVERPAID   {names:25s} {got:.0f} of {expected:.0f} (+{got-expected:.0f})")

    if other[month]:
        print("  -- other transfers from tenants --")
        for iban, amount, text in other[month]:
            name = tenants[iban][0]["tenant"]
            print(f"  {name:20s} {amount:8.2f}  {text}")