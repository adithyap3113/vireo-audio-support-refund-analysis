# Vireo Audio - Support Refund Control

## What this is
A small local, AI-assisted support-refund analysis tool for the Vireo Audio Set C assessment.
It reconciles the helpdesk export, removes migration duplicates, normalizes legacy monetary values, produces monthly refund views by reason and agent, and adds a local ML review queue for `GW-OTHER` tickets that look like standard reason codes.

## Quick start on a clean machine

Requirements: Python 3.10+.

```bash
python -m venv .venv
# Windows CMD
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

The raw pack files are under `data/raw/`. No paid API call is required.

For a non-UI run:

```bash
python vireo_analysis.py
```

Tests:

```bash
python -m unittest -q test_vireo_analysis.py
```

## Key decisions

1. **Deduplicate by `ticket_id`.** There are 638 IDs repeated once under both `helpdesk` and `legacy_fd`; all non-monetary fields match. When both exist, the helpdesk row is retained.
2. **Normalize legacy money by /100.** The policy says legacy monetary values use the legacy native unit. Paired legacy/helpdesk tickets match exactly after dividing the legacy value by 100. This is an inference from the data, not a sentence in the policy.
3. **Do not treat all `GW-OTHER` rows as true goodwill.** The code is a dropdown selection and the free text often describes standard reasons. The AI queue is a review aid, not an automatic recode or automatic savings claim.
4. **Do not rank agents as misconduct.** Returns Desk is expected to process the majority of refunds and Tier 2 is explicitly not comparable with Tier 1 on volume.
5. **Do not infer causality from Q4.** Q4 refund spend increased because ticket volume increased, while refund rate actually declined vs Q3 in this dataset.

## Headline numbers

- Raw rows: 12,238
- Unique tickets after migration dedupe: 11,600
- Refund tickets after dedupe: 2,340
- Raw exported refund sum: ₹2.30Cr
- Reconciled refund sum: ₹67.10L over 18 months (~₹11.18L/quarter)
- Q3 2025 refund rate: 21.98% (~22.0%)
- Proposed operating target: 15.0% (a business-case target, not a Vireo policy threshold)
- At 650 tickets/week, 22.0% -> 15.0% corresponds to ~589 fewer refunds/quarter and about ₹16.9L/quarter of potential refund-spend reduction using the observed average refund value. This is a business-case sensitivity, not a forecast.
- Refund + replacement occurred on 166 tickets. Refunds on those tickets were ₹5.74L; estimated replacement cost per policy adds ₹2.97L; combined exposure ₹8.71L.
- 879 tickets were recorded as `GW-OTHER` above the ₹500 goodwill cap, tagged value ₹28.72L. This is a review signal because the dropdown code may be wrong.
- The local reason model agreed with existing non-GW labels on 91.1% of a held-out test set. It then flagged 162 high-confidence `GW-OTHER` tickets for review, totaling ₹4.52L.

## Known limitations

- The policy does not publish the legacy currency conversion factor. `/100` is inferred from exact paired rows and the resulting reconciliation to Vireo's ~₹11L/quarter email reference.
- `orders.csv` has no delivery timestamp, so the 7-day DOA window cannot be independently verified.
- Dispatch status is not a column, so `CANCEL` before dispatch cannot always be audited from reference data alone.
- The local classifier is intentionally a review aid. It does not claim ground truth for historical reason codes.
- No paid LLM API is required; the tool uses a local TF-IDF + logistic regression model. That makes tool call cost ₹0.
