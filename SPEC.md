# Killisfeldstraße 27+29 — property operations system

16 units (15 let, 1 vacant: 29 EG links) plus garages, Karlsruhe-Durlach.
Built and operated by me; my father is the owner and data source.

## Project 1 — Rent reconciliation (running since 5 Nov 2026)
- In: Sparkasse MT940 export, tenants.csv (payer IBAN, expected total, valid_from)
- Match by IBAN, not name. Expected per tenant per month; later rows replace earlier.
- Outcomes: ok (±10 €) / underpaid / overpaid / missing. Rent due 3rd working day.
- Known rules: Azal 1450 is correct; Hirmer +47/month is a held credit; Kaya garage 45 € from same account.
- Backlog: payments in last 3 days count for next month (Rashidi M.); separate
  Heizkosten/Nachzahlung lump sums from rent; tolerance_over column; garage rows; monthly PDF/WhatsApp summary.
- First run: 15/15 tenants matched for Sep–Oct; 9 anomalies flagged, 2 real, 7 missing rules.

## Project 2 — Repair & request tracker (Dec 2026)
- Tenant emails/WhatsApp → classify (repair / payment / question / other) with Claude
- Eval set: data/emails_labelled.csv, 20 hand-labelled; measured per category
- Tickets with status; draft reply in owner's voice; reminder if open > 14 days
- Ticket #1: Braun, balcony, pays "unter Vorbehalt"

## Project 3 — Dashboard & automation (Jan–Feb 2027)
- Scheduled run, WhatsApp alerts, FastAPI + Postgres, dashboard for all units
- Mietspiegel gap analysis per flat

## Private data
tenants.csv and bank exports are gitignored.