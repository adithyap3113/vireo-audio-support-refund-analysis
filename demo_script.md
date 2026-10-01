# 3-minute recording script

**0:00-0:30 - Problem**
"Arjun's export is inflated. I start with 12,238 rows, but there are 638 migration duplicates. The legacy file also stores monetary values in a native unit. Paired rows show the legacy amount is exactly 100x the helpdesk amount, so I normalize by 100 and retain one canonical ticket."

**0:30-1:10 - What changed between versions**
"Version 1 was just a grouped refund report. I narrowed the ask to a reconciled board-pack view because the export itself was wrong. I added the duplicate and currency controls first. I also stopped short of a simple 'bad agent' ranking because the policy says Returns Desk is designed to process most refunds and Tier 2 should not be compared with Tier 1 on volume."

**1:10-1:50 - AI-assisted part**
"The second layer is local ML. I train a TF-IDF plus logistic-regression classifier on standard, non-GW refund reasons, then score GW-OTHER tickets. It is deliberately a review queue, not an automatic recoder. On a held-out set it agrees with the existing standard labels 91.1% of the time."

**1:50-2:30 - Business outcome**
"After cleanup, refund spend is ₹67.10 lakh over 18 months, about ₹11.18 lakh per quarter, which matches the finance email's rough ₹11 lakh. Q3 2025 is 21.98% refund rate. Using 15% as the proposed operating target and 650 tickets a week, the sensitivity is about ₹16.9 lakh of refund spend per quarter. Separately, 166 tickets gave both a refund and a replacement, with ₹8.71 lakh combined exposure under the policy cost standard."

**2:30-3:00 - What I threw away / limitations**
"I did not build a paid LLM workflow, a causal model, or automated refund actioning. I left those out because they add risk without improving the board-pack decision in a five-hour cap. I also document that the legacy conversion factor is inferred, DOA timing cannot be fully verified because delivery time is missing, and the AI queue still needs human review."
