# flats-automation

Rent reconciliation and tenant-request tracking for a 16-unit residential portfolio
in Karlsruhe (two buildings, plus garages). Built and operated by me; Replaces a paper-and-memory process.

## The problem
15 tenants, rent arriving on different days into one Sparkasse account mixed with
private and business transfers. Checking who paid took an afternoon with paper
statements, and the owner's own records had wrong rents for 2 tenants and a wrong
surname for 1.

## What it does (v1, 6 Nov 2026)
- Parses the bank's MT940 export (wrapped lines, `:61:`/`:86:` fields)
- Matches transfers to tenants by **IBAN**, not name (payers include partners,
  relatives and a different surname for one flat)
- Expected amount per tenant with `valid_from`, so rent changes are versioned
- Separates rent from one-off transfers (Heizkosten, Nachzahlungen) by purpose
  text or amount match
- Payments in the last 3 days of a month count for the next month
- Outcomes per tenant per month: ok / underpaid / overpaid / missing (±10 € tolerance)
- Writes one CSV per month to `output/` for downstream reporting

## Result
First run on Sep–Oct 2026: 15/15 tenants matched, 9 anomalies flagged.
After encoding three rules: 1 anomaly left (a known, intentional overpayment).
Reconciling a month now takes 3 minutes instead of 2 afternoons.

## Next
- Garages as additional tenant rows
- Lateness per tenant (`due_day` + 3-day buffer), monthly summary to the owner
- Tenant-request triage with Claude, scored against `data/emails_labelled.csv`
  (20 hand-labelled emails)
- Scheduled run, WhatsApp alerts, dashboard

## Run
    python3 rent_check.py

Real tenant and bank data are gitignored; `data/emails_labelled.csv` is synthetic.