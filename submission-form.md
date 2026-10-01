# Vireo Audio - Submission Form

## What did you build, and what business outcome does it move? State the number and the money.

I built a local, AI-assisted refund-control tool that reconciles the support export, removes migration duplicates, normalizes the legacy monetary unit, produces monthly refund views by reason and agent, and adds an AI review queue for suspicious `GW-OTHER` coding.

Q3 2025 refund rate is 21.98% (~22%). Using a proposed 15% management target and Vireo's stated 650 tickets/week, the sensitivity is ~589 fewer refunds per quarter and **about ₹16.9 lakh potential refund-spend reduction per quarter** at the observed average refund value.

A separate direct control opportunity is **₹8.71 lakh combined exposure** across 166 tickets where both refund and replacement were issued.

## What does one run cost, and what would a month cost at Vireo's volume (roughly 650 tickets a week)? Show the arithmetic. If you used no paid calls, say so.

**Paid calls: ₹0.** The tool uses a local TF-IDF + logistic-regression model and local CSV/PDF inputs.

650 tickets/week × 4.33 weeks/month ≈ 2,817 tickets/month.

Paid API calls/run = 0.
Therefore estimated paid model cost/month at Vireo volume = **₹0** (excluding the machine used to run the tool).

## How do you know it works? Sample size, how you checked, error rate, and the kind of case it gets wrong.

The reconciliation layer is deterministic: 12,238 rows -> 11,600 unique ticket IDs; 638 migration duplicate pairs; 0 normalized monetary mismatches across duplicate pairs; final refund total ₹67,09,932.

For the AI reason layer, the model is trained only on non-GW reason codes. Held-out agreement with the recorded standard labels is **91.1%**. This is label agreement, not proof of ground truth. Errors are concentrated in DOA/warranty cases where the same free text can describe a fault, replacement, warranty buy-back, or a refund-delay follow-up.

## Did you change, narrow, or push back on the client's ask? What, when, and why?

Yes. I changed the first-pass interpretation of "who is giving away money" from a simple agent ranking to a reconciled view plus policy-control analysis. Returns Desk is designed to process most refunds, and Tier 2 is explicitly not comparable with Tier 1 on volume, so raw volume would be misleading.

I also pushed back on the interpretation that Q4 refund behaviour worsened because frontline stopped arguing. Refund spend rose, but refund rate fell 1.74 percentage points from Q3; the full data shows only a 0.03 CSAT increase.

## What is wrong with what you are handing us? Be specific.

- The /100 legacy monetary conversion is inferred from paired rows and reconciliation because the policy does not state the conversion factor.
- Delivery timestamps are absent, so the 7-day DOA rule cannot be fully audited.
- Dispatch status is absent, so some cancellation eligibility cannot be independently verified.
- The AI reason assistant is a review aid, not ground truth or automatic recoding.
- The tool is local and does not write back to the helpdesk.

## What did you deliberately leave out, and why that rather than something else?

I left out a paid LLM workflow, causal attribution, automatic refund decisions, and a production database. The task is a five-hour decision-support exercise; those additions would increase build and operational risk without improving the immediate board-pack question.

## Anything you built or found that nobody asked for?

Yes: a policy-exception view for refund + replacement, an AI review queue for `GW-OTHER` tickets, and a reconciliation check that independently explains the Finance vs helpdesk total discrepancy.

## What did you use AI for? Which tools and models, where they helped, where they wasted your time, what you threw away. Link your three-minute screen recording here.

AI tools were used for implementation and review. The submitted tool itself uses a local TF-IDF + logistic-regression model; no paid model call is required.

**Screen recording:** [PASTE PUBLIC GOOGLE DRIVE LINK HERE]

## Public Google Drive Link

[PASTE PUBLIC GOOGLE DRIVE LINK HERE]

## Someone picks this up on Monday and you are unreachable. The three things they need to know.

1. Run `pip install -r requirements.txt`, then `streamlit run app.py`.
2. The first job is data reconciliation: dedupe by `ticket_id`, prefer helpdesk where paired, and normalize legacy refund values by /100.
3. Treat the AI `GW-OTHER` queue as a human-review list, not automatic recoding or automatic savings.

## Honest hours spent.

**5 hours**
