# Killisfeldstraße 27+29 — Automation

## Problem
Father manages two buildings by email and phone. Tenants pay late, repair
requests get forgotten, tenants ask again. He says 5 h/month; real number
unknown until the bank CSV says.

## Project 1 — Rent monitoring
- In: Sparkasse CSV export (90 days) + tenant list (flat, name, rent, due day)
- Does: match every transfer to a tenant → paid / unpaid per flat per month
- Out: on the 3rd, WhatsApp to father: "Flat 2 and 5 haven't paid."
       Draft reminder email in his Drafts. Nothing sent automatically.

## Project 2 — Repair tracker
- In: tenant emails
- Does: classify (repair / follow-up / rent question / other), log repairs
  in a sheet with status, draft a reply in his voice, look up status on follow-ups
- Out: draft in Drafts + WhatsApp ping. Reminder to him if a repair is open > 14 days.

## Rules
- He only answers yes/no. Email and WhatsApp only, no new apps.
- Nothing goes to a tenant without his confirmation (first two months).
- Unsure → do nothing and say so.

## Need from him
- Last 3 months Sparkasse CSV
- Tenant list with amounts and due days
- 20–30 old tenant emails (later)