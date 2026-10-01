# Board-pack snapshot

## Reconciled position
- 12,238 source rows -> 11,600 unique tickets; 638 migration duplicates removed.
- Raw exported refund sum: Rs 23.01Cr; reconciled total: Rs 67.10L over 18 months (~Rs 11.18L per quarter).
- Q3 2025 refund rate: 21.98%; Q4: 20.24%.

## Monthly / reason output
Use outputs/monthly_refunds_by_reason.csv for the full board table. Each value is refund rupees after dedupe and legacy normalization.

## Agent spend - context matters
Top agents by refund amount are shown for operational investigation, not as misconduct rankings. Returns Desk is designed to process most refunds; Tier 2 is not comparable with Tier 1 on volume.

| Agent | Team | Refund tickets | Refund amount | Refund rate | Double awards |
|---|---|---:|---:|---:|---:|
| A3036 Ritika D'Souza | Returns Desk | 266 | Rs 7.74L | 50.6% | 8 |
| A3035 Dev Kulkarni | Billing | 235 | Rs 6.28L | 33.7% | 1 |
| A3030 Aishwarya Trivedi | Logistics | 162 | Rs 5.07L | 17.2% | 27 |
| A3038 Ankit Dhillon | Returns Desk | 171 | Rs 4.90L | 53.1% | 1 |
| A3037 Manish Iyer | Returns Desk | 175 | Rs 4.29L | 47.7% | 5 |
| A3032 Sneha Bansal | Billing | 126 | Rs 3.38L | 40.1% | 2 |
| A3033 Vikram Banerjee | Billing | 113 | Rs 3.24L | 35.3% | 0 |
| A3034 Tanvi Rathore | Billing | 118 | Rs 2.90L | 38.4% | 0 |
| A3018 Krishna Bhatt | Email Frontline | 87 | Rs 2.31L | 11.1% | 7 |
| A3026 Aadhya Deshpande | Voice Frontline | 65 | Rs 1.94L | 12.9% | 8 |

## Direct policy-control finding
166 tickets contain both a refund and a replacement. Refunds total Rs 5.74L; policy replacement cost adds Rs 2.97L; combined exposure is Rs 8.71L.

## AI review signal
The local model agrees with recorded non-GW labels on 91.1% of a held-out set. It flags 162 GW-OTHER tickets at >=80% confidence for possible standard-reason recoding, totaling Rs 4.52L.

## Business case
Using Q3 2025's 21.98% as the observed ~22% baseline and 15% as a proposed management target, 650 tickets/week implies ~8,450 tickets/quarter. The gap is ~589 refunds/quarter; at the observed average refund value, that is about Rs 16.90L potential refund-spend reduction per quarter. This is a sensitivity, not a forecast.