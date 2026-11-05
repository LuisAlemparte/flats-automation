import re

with open("data/umsaetze.txt", encoding="utf-8") as f:
    raw = f.read()

# 1. Glue wrapped lines back together
lines = []
for line in raw.splitlines():
    if line.startswith(":"):
        lines.append(line)
    elif lines:
        lines[-1] += line

# 2. Walk the lines, pair each :61: with its :86:
payers = {}
amount = 0
for line in lines:
    if line.startswith(":61:"):
        m = re.search(r"([CD])R?([\d,]+)", line[10:])
        amount = float(m.group(2).replace(",", "."))
        if m.group(1) == "D":
            amount = -amount
    elif line.startswith(":86:") and amount > 0:
        fields = dict(re.findall(r"\?(\d\d)([^?]*)", line))
        name = fields.get("32", "") + fields.get("33", "")
        iban = fields.get("31", "")
        payers[iban] = name

for iban, name in sorted(payers.items(), key=lambda p: p[1]):
    print(f"{name:45s} {iban}")