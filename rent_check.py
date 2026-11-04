import csv
tenants = {"Schmidt": 850, "Yilmaz": 920, "Braun": 780, "Keller": 690}
paid = set()

with open("data/umsaetze.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter=";")

    for row in reader:
        amount = float(row["Betrag"].replace(",", "."))
        if 300 <=amount <= 2000 and "Miete" in row["Verwendungszweck"]:
            print(row["Beguenstigter/Zahlungspflichtiger"], amount)
            for surname in tenants:
                if surname in row["Beguenstigter/Zahlungspflichtiger"]:
                    expected = tenants[surname]
                    if abs(amount - expected) <=10:
                        paid.add(surname)
                    elif amount < expected - 10:
                        print(f"UNDERPAID: {surname} paid{amount} of {expected}")
for name in tenants:
    if name not in paid:
        print(f"MISSING: {name} ({tenants[name]} €)")