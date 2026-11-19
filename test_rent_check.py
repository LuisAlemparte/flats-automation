from rent_check import classify_transfers

# Invented tenants: iban -> list of rows (same shape as tenants.csv rows)
tenants = {
    "DE11": [{"house": "27", "flat": "EG", "tenant": "Test A", "iban": "DE11",
              "expected": "500", "valid_from": "2026-08-01", "due_day": "3"}],
    "DE22": [{"house": "27", "flat": "1.OG", "tenant": "Test B", "iban": "DE22",
              "expected": "600", "valid_from": "2026-08-01", "due_day": "3"}],
    "DE33": [{"house": "27", "flat": "2.OG", "tenant": "Test C", "iban": "DE33",
              "expected": "600", "valid_from": "2026-08-01", "due_day": "3"}],
}

# Invented transfers: A pays rent on the 2nd, B pays nothing, A also pays 120 Heizkosten
transactions = [
    {"month": "2026-10", "day": 2, "amount": 500.0, "iban": "DE11", "text": "Miete Oktober"},
    {"month": "2026-10", "day": 15, "amount": 120.0, "iban": "DE11", "text": "Heizkosten"},
    # C: 590 for an expected 600 (tolerance), capital MIETE in November, a refund that must be ignored
    {"month": "2026-10", "day": 4, "amount": 590.0, "iban": "DE33", "text": "Ueberweisung"},
    {"month": "2026-11", "day": 1, "amount": 600.0, "iban": "DE33", "text": "MIETE NOVEMBER"},
    {"month": "2026-10", "day": 9, "amount": -50.0, "iban": "DE33", "text": "Rueckbuchung"},
]

received, paid_on, other = classify_transfers(transactions, tenants)

assert received[("DE11", "2026-10")] == 500.0          # rent counted
assert ("DE22", "2026-10") not in received             # B paid nothing
assert paid_on[("DE11", "2026-10")] == 2               # paid on the 2nd
assert other["2026-10"] == [("DE11", 120.0, "Heizkosten")]  # Heizkosten is "other"

assert received[("DE33", "2026-10")] == 590.0            # within tolerance → rent
assert received[("DE33", "2026-11")] == 600.0               # capital MIETE still matches
assert all(amount > 0 for _, amount, _ in other["2026-10"])   # negative ignored
assert ("DE33", "2026-10") in received and received[("DE33", "2026-10")] != 540.0   # -50 not subtracted
print("classify_transfers: 8 checks passed")


