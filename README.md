# flats-automation

Rent reconciliation, monthly owner report and tenant-request handling for a
16-unit residential portfolio in Karlsruhe (two buildings plus 17 garages).
Built and operated by me for my father, the owner. Replaces a paper-and-memory process.

## The problem
28 payers (15 flats, 13 garages), rent arriving on different days into one
Sparkasse account mixed with private and business transfers. Checking who paid
took an afternoon with paper statements. The owner's own sheet had wrong rents for
2 flats and 8 garages, one wrong surname, and no record of *when* people paid.

## What it does

**`rent_check.py` — reconciliation (since 5 Nov 2026)**
- Parses the bank's MT940 export (wrapped lines, `:61:`/`:86:` fields)
- Matches transfers to tenants by **IBAN**, not name (payers include partners,
  relatives and a different surname for one flat)
- Expected amount per tenant with `valid_from`, so rent changes are versioned
- Separates rent from one-off transfers (Heizkosten, Nachzahlungen) by purpose text or amount
- Payments in the last 3 days of a month count for the next month
- Per-tenant `due_day` + 3-day buffer → `days_late`; status ok / LATE / UNDERPAID / OVERPAID / MISSING
- Writes one CSV per month and a one-page German owner report
  (`output/Bericht-YYYY-MM.md`: Soll/Ist, Auffälligkeiten, offene Anliegen)

**`classify_emails.py` — tenant requests (since 9 Nov 2026)**
- `inbox`: classifies new tenant emails with Claude Haiku into
  repair / payment / question / other and appends them to a ticket list (deduplicated)
- `close <id>`: marks a ticket done
- `reply <id>`: drafts a reply in the owner's voice with Claude Sonnet (firm, polite,
  cites the contract, never invents deadlines or firms) and saves it to `output/antworten/`
- no argument: runs the eval below


**`build_db.py` + `queries.sql` — SQL layer (since 12 Nov 2026)**
- `build_db.py` rebuilds `data/flats.db` (SQLite) from the CSVs and the bank export:
  tables `tenants`, `transactions`, `tickets`
- `queries.sql` holds the questions the owner asks, as plain SQL:
  rent per tenant per month with status (one query, verified row-for-row against `rent_check.py`),
  lateness history per tenant, open tickets by category
- New questions are a query, not a script: "who has paid late more than once since August?" is five lines

## Results
- Sep–Oct 2026: 28/28 payers matched. 9 anomalies flagged on the first run; after
  encoding three rules, 1 known credit remained. Two garages found not paying for 3 months.
- Reconciling a month: **3 minutes instead of 2 afternoons** (owner's words).
- Lateness data contradicted the owner's impression: 26 of 28 pay on time; two don't.
- The SQL lateness query found a third sheet error: a garage tenant recorded as "never pays" pays two months at a time, for a different garage number than the sheet says.

## The eval, and what it taught me
`data/emails_labelled.csv`: 30 hand-labelled German/English tenant emails, including
mixed-topic, angry and ambiguous ones.

| step | change | score |
|---|---|---|
| v1 | 20 easy emails, 3-line prompt | 19/20 |
| v1 | +10 hard emails | 27/30 |
| v2 | category definitions in prompt | 27/30 — fixed 2, **broke 2** |
| v2.1 | removed an over-specific rule, fixed 2 wrong labels | 30/30 |
| model | Haiku 4.5 → 5.5 | 22/30 — all misses were *empty* answers |
| fix | token budget for thinking, log unexpected output | 30/30 |

Lessons: a prompt change can trade failures for failures at the same score, so
keep the whole set. Misses split into label errors and prompt errors; fix each
where it lives. A silent fallback turned a bug into a "model got worse" story.
Runs aren't deterministic; a score is a snapshot.

## Next
- Treppenhausreinigung case: contract review for 10 flats, templated letters
- Scheduled monthly run, WhatsApp delivery of the report
- Dashboard across all units, Mietspiegel gap per flat

## Run
    python3 rent_check.py
    python3 classify_emails.py            # eval
    python3 classify_emails.py inbox      # new emails → tickets
    python3 classify_emails.py reply 4    # draft a reply

Needs `ANTHROPIC_API_KEY` in `.env`. Real tenant and bank data are gitignored;
`data/emails_labelled.csv` is synthetic.
## Thu 12 Nov — Week 7 (SQL)
- Psets: songs 8/8, movies 14/14, fiftyville 3/3 (Bruce, New York City, Robin), all before 13:30
- SELECT/WHERE/ORDER BY/LIMIT, COUNT/AVG/SUM, LIKE '%x%', nested SELECT ... IN (...), JOIN ... ON, DISTINCT
- Two prompts: $ = shell, sqlite> = database. .schema/.tables/.quit only inside; cat file | sqlite3 db from outside
- Flats: build_db.py → flats.db (tenants, transactions, tickets). Rent check as one query with WITH (CTE), LEFT JOIN, COALESCE, CASE WHEN; matches rent_check.py row for row
- Lateness query: SUBSTR to cut the day out of a date, HAVING for grouped rows. Found Kaya S.O. pays 100 every 2 months for garage 5, sheet says 45 for garage 3