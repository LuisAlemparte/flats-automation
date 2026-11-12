"""Build data/flats.db from tenants.csv, the MT940 bank export and tickets.csv.

Run:  python3 build_db.py
Then: sqlite3 data/flats.db
"""
import csv
import os
import re
import sqlite3

DB = "data/flats.db"

# Start fresh every run: the CSVs are the source of truth, the db is derived.
if os.path.exists(DB):
    os.remove(DB)
con = sqlite3.connect(DB)
cur = con.cursor()

cur.executescript("""
CREATE TABLE tenants (
    id INTEGER PRIMARY KEY,
    house TEXT,
    flat TEXT,
    tenant TEXT,
    payer_name TEXT,
    iban TEXT,
    kalt REAL,
    nk REAL,
    expected REAL,
    valid_from TEXT,
    due_day INTEGER,
    notes TEXT
);
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY,
    date TEXT,
    month TEXT,
    amount REAL,
    iban TEXT,
    name TEXT,
    text TEXT
);
CREATE TABLE tickets (
    id INTEGER PRIMARY KEY,
    date TEXT,
    tenant TEXT,
    category TEXT,
    status TEXT,
    text TEXT
);
""")

# --- tenants ---------------------------------------------------------------
with open("data/tenants.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f, delimiter=";"):
        cur.execute(
            "INSERT INTO tenants (house, flat, tenant, payer_name, iban, kalt, nk, expected, valid_from, due_day, notes) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (r["house"], r["flat"], r["tenant"], r["payer_name"], r["iban"],
             float(r["kalt"]), float(r["nk"]), float(r["expected"]),
             r["valid_from"], int(r["due_day"] or 3), r["notes"]),
        )

# --- transactions (same MT940 parsing as rent_check.py) --------------------
with open("data/umsaetze.txt", encoding="utf-8") as f:
    raw = f.read()
lines = []
for line in raw.splitlines():
    if line.startswith(":"):
        lines.append(line)
    elif lines:
        lines[-1] += line

current = None
for line in lines:
    if line.startswith(":61:"):
        d = line[4:10]
        year, mon, day = int("20" + d[:2]), int(d[2:4]), int(d[4:6])
        date = f"{year}-{mon:02d}-{day:02d}"
        # payments in the last days of a month count for the next month
        if day >= 29:
            mon += 1
            if mon == 13:
                mon, year = 1, year + 1
        month = f"{year}-{mon:02d}"
        m = re.search(r"([CD])R?([\d,]+)", line[10:])
        amount = float(m.group(2).replace(",", "."))
        if m.group(1) == "D":
            amount = -amount
        current = [date, month, amount, "", "", ""]
    elif line.startswith(":86:") and current:
        fields = dict(re.findall(r"\?(\d\d)([^?]*)", line))
        current[3] = fields.get("31", "")
        current[4] = fields.get("32", "")
        current[5] = fields.get("20", "")
        cur.execute("INSERT INTO transactions (date, month, amount, iban, name, text) VALUES (?,?,?,?,?,?)", current)
        current = None

# --- tickets ---------------------------------------------------------------
if os.path.exists("data/tickets.csv"):
    with open("data/tickets.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter=";"):
            cur.execute("INSERT INTO tickets (id, date, tenant, category, status, text) VALUES (?,?,?,?,?,?)",
                        (int(r["id"]), r["date"], r["tenant"], r["category"], r["status"], r["text"]))

con.commit()
for table in ("tenants", "transactions", "tickets"):
    n = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"{table:13s} {n:4d} rows")
con.close()
