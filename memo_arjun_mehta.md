# Memo - Arjun Mehta, Finance Controller

**Subject: Vireo Audio refund controls - reconciled monthly view and action case**

The export is overstating refund spend. The 18-month file has 12,238 rows but only 11,600 unique tickets because 638 migrated tickets appear once in each source system. Legacy monetary values are also stored in a native unit; paired tickets show a consistent 100:1 relationship to helpdesk rupees. After deduplication and normalization, refund spend is **₹67.1 lakh over 18 months, about ₹11.18 lakh per quarter**, which is consistent with the helpdesk reference in the email thread.

The main operating measure I would use is refund rate, not raw quarterly rupees. **Q3 2025 was 21.98% (about 22%)**. I would use **15% as a management target** for the business case, not as a policy limit. At Vireo's stated 650 tickets/week, the gap is roughly 589 fewer refunds per quarter. Using the observed average refund of about ₹2,867, that is **about ₹16.9 lakh of potential refund-spend reduction per quarter** if the mix and average refund stay similar.

The data also identifies a direct control issue: **166 tickets gave both a refund and a replacement**. Under the policy cost standard, those tickets represent ₹5.74 lakh of refund plus an estimated ₹2.97 lakh of replacement cost, or **₹8.71 lakh of combined exposure**. That is a cleaner immediate control than blaming refund volume on individual agents.

There is also a coding problem. **879 tickets are recorded as GW-OTHER above ₹500**, but the free text frequently describes ordinary cancellation, return, payment, transit, or warranty reasons. I therefore built an AI review queue rather than calling these all "bad refunds". A local model trained on the standard reason codes agrees with their recorded labels on 91.1% of a held-out set and flags 162 high-confidence GW-OTHER cases (₹4.52 lakh) for human review.

The Q4 story is more nuanced than the email thread suggests. Refund spend rose from ₹12.07 lakh in Q3 to ₹16.28 lakh in Q4, but refund rate fell from 21.98% to 20.24%. Overall CSAT rose only 0.03 in the full responding population. The dataset therefore shows higher spend driven more by volume than by a higher refund propensity; it does not establish the claimed +0.4 CSAT improvement.

**Recommended board-pack action:** set the 15% refund-rate target as a monitored operating case, enforce the no-refund-plus-replacement control, and use the AI review queue to clean GW-OTHER coding before changing frontline policy.

**Important limitations:** the legacy /100 conversion is inferred from duplicate pairs and reconciliation because the policy does not state the factor explicitly; delivery timestamps are absent so the 7-day DOA rule cannot be fully audited; dispatch status is absent so some cancellation eligibility cannot be independently verified.
