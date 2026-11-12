-- Rent check for one month: expected vs received per tenant, with status.
-- Rules match rent_check.py: latest valid_from row per flat; a transfer counts
-- as rent if its text contains 'miete' or its amount is within 10 € of expected.
WITH active AS (
    SELECT * FROM tenants t
    WHERE valid_from <= '2026-10-31'
      AND valid_from = (SELECT MAX(valid_from) FROM tenants
                        WHERE flat = t.flat AND house = t.house AND valid_from <= '2026-10-31')
),
rent AS (
    SELECT a.tenant, SUM(x.amount) AS received
    FROM active a
    JOIN transactions x ON x.iban = a.iban
    WHERE x.month = '2026-10' AND x.amount > 0
      AND (LOWER(x.text) LIKE '%miete%' OR ABS(x.amount - a.expected) <= 10)
    GROUP BY a.tenant
)
SELECT
    a.tenant,
    a.expected,
    ROUND(COALESCE(r.received, 0)) AS received,
    CASE
        WHEN r.received IS NULL THEN 'MISSING'
        WHEN ABS(r.received - a.expected) <= 10 THEN 'ok'
        WHEN r.received < a.expected THEN 'UNDERPAID'
        ELSE 'OVERPAID'
    END AS status
FROM active a
LEFT JOIN rent r ON r.tenant = a.tenant
ORDER BY status, a.tenant;