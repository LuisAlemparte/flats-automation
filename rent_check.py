import csv
import os
import re
from collections import defaultdict
BUFFER = 3 # days after due_day before a payment counts as late

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
        paid_day = day
        if day >= 29:
            paid_day = 0
            mon += 1
            if mon == 13:
                mon = 1 
                year += 1
        month = f"{year}-{mon:02d}"
        m = re.search(r"([CD])R?([\d,]+)", line[10:])
        amount = float(m.group(2).replace(",", "."))
        if m.group(1) == "D":
            amount = -amount
        transactions.append({"month": month, "day": paid_day, "amount": amount, "iban": "", "text": ""})
    elif line.startswith(":86:") and transactions:
        fields = dict(re.findall(r"\?(\d\d)([^?]*)", line))
        transactions[-1]["iban"] = fields.get("31", "")
        transactions[-1]["text"] = fields.get("20", "")

print(len(transactions), "transactions")

# Sort each tenant transfer into rent or other
received = defaultdict(float)
paid_on = defaultdict(int)
other = defaultdict(list)
for t in transactions:
    if t["amount"] <= 0 or t["iban"] not in tenants:
        continue
    expected_any = [float(r["expected"]) for r in tenants[t["iban"]]]
    is_rent = "miete" in t["text"].lower() or any(abs(t["amount"] - e) <= 10 for e in expected_any)
    if is_rent:
        received[(t["iban"], t["month"])] += t["amount"]
        paid_on[(t["iban"], t["month"])] = max(paid_on[(t["iban"], t["month"])], t["day"])
    else:
        other[t["month"]].append((t["iban"], t["amount"], t["text"][:50]))

STATUS_DE = {"MISSING": "FEHLT", "LATE": "VERSPÄTET", "UNDERPAID": "ZU WENIG", "OVERPAID": "ZU VIEL"}


def write_report(month, results, extras):
    total_expected = sum(r["expected"] for r in results)
    total_got = sum(r["got"] for r in results)
    problems = [r for r in results if r["status"] != "ok"]
    lines = [f"# Mietbericht {month}", ""]
    lines.append(f"**Soll:** {total_expected:,.0f} €  **Ist:** {total_got:,.0f} €  **Differenz:** {total_got - total_expected:+,.0f} €".replace(",", "."))
    lines.append(f"**Mieter:** {len(results)}  **ohne Auffälligkeit:** {len(results) - len(problems)}")
    lines += ["", "## Auffälligkeiten", ""]
    if not problems:
        lines.append("Keine.")
    for r in problems:
        detail = f"{r['got']:.0f} von {r['expected']:.0f} €"
        if r["status"] == "LATE":
            detail += f", {r['days_late']} Tage zu spät"
        lines.append(f"- **{STATUS_DE[r['status']]}** {r['name']}: {detail}")
    if extras:
        lines += ["", "## Sonstige Eingänge von Mietern", ""]
        for iban, amount, text in extras:
            lines.append(f"- {tenants[iban][0]['tenant']}: {amount:.2f} € ({text.replace('SVWZ+', '')})")
    if os.path.exists("data/tickets.csv"):
        open_tickets = [t for t in csv.DictReader(open("data/tickets.csv", encoding="utf-8"), delimiter=";") if t["status"] == "open"]
        lines += ["", f"## Offene Anliegen ({len(open_tickets)})", ""]
        for t in open_tickets:
            lines.append(f"- #{t['id']} {t['date']} {t['tenant']} [{t['category']}]: {t['text'][:80]}")
    with open(f"output/Bericht-{month}.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


# Compare per month, per tenant
months = sorted({t["month"] for t in transactions})[1:-1]
os.makedirs("output", exist_ok=True)
for month in months:
    print(f"\n=== {month} ===")
    results = []
    out = open(f"output/{month}.csv", "w", encoding="utf-8", newline="")
    writer = csv.writer(out, delimiter=",")
    writer.writerow(["tenant", "expected", "recieved", "status", "difference", "days_late"])
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
        due = int(active[0]["due_day"])
        days_late = max(0, paid_on[(iban, month)] - due - BUFFER)
        if got == 0:
            status = "MISSING"
        elif abs(got - expected) <= 10 and days_late > 0:
            status = "LATE"
        elif abs(got - expected) <= 10:
            status = "ok"
        elif got < expected:
            status = "UNDERPAID"
        else:
            status = "OVERPAID"
        print(f"{status:10s} {names:25s} {got:.0f} of {expected:.0f}   paid day {paid_on[(iban, month)]:2d}  late {days_late}")
        results.append({"name": names, "expected": expected, "got": got, "status": status, "days_late": days_late})
        writer.writerow([names, f"{expected:.0f}", f"{got:.0f}", status, f"{got - expected:.0f}", days_late])
    out.close()
    write_report(month, results, other[month])
    if other[month]:
        print("  -- other transfers from tenants --")
        for iban, amount, text in other[month]:
            name = tenants[iban][0]["tenant"]
            print(f"  {name:20s} {amount:8.2f}  {text}")