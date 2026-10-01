# Validation report

## Reconciliation tests

- 12,238 raw support rows.
- 11,600 unique ticket IDs.
- 638 duplicate ticket IDs / 638 extra rows.
- Duplicate pairs are identical on every non-monetary field.
- Legacy monetary values divided by 100 match helpdesk values exactly on duplicate pairs.
- Post-cleanup refund total: ₹6,709,932 across 2,340 refund tickets.
- Average quarterly refund total: ₹1,118,322, consistent with the email thread's ~₹11 lakh/quarter reference.

## Policy-control checks

- Refund amount greater than matched order value: 0.
- Refund + replacement: 166 tickets; ₹574,191 refund + ₹296,970 replacement cost = ₹871,161 exposure.
- Recorded GW-OTHER above ₹500: 879 tickets; ₹2,871,632 tagged value.

## AI reason QA

The AI assistant is trained only on standard non-GW reason labels to avoid teaching the model that the noisy `GW-OTHER` code is the truth.

- Hold-out agreement with recorded standard labels: 91.1%.
- High-confidence threshold: 80%.
- GW-OTHER tickets above threshold: 162.
- Value of those review-queue tickets: ₹451,765.

This is label agreement and prioritization performance, not proof of ground-truth reason accuracy. Historical dropdown codes can themselves be wrong.

## Q4 client-claim check

Q3 2025: refund rate 21.98%, refund spend ₹12.07L, CSAT 3.48.
Q4 2025: refund rate 20.24%, refund spend ₹16.28L, CSAT 3.51.

Therefore refund spend rose 34.8% while refund rate fell 1.74 percentage points. Overall CSAT increased 0.03, not 0.4, in the full ticket population with responses.
