from pathlib import Path
import sys
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from vireo_analysis import run_analysis

st.set_page_config(page_title="Vireo Audio - Refund Control", layout="wide")

@st.cache_data(show_spinner=False)
def get_result():
    return run_analysis()

result = get_result()
h = result["headline"]

st.title("Vireo Audio - Refund Control")
st.caption("Cleaned monthly refund reporting, agent view, and AI-assisted reason QA")

c1, c2, c3, c4 = st.columns(4)
c1.metric("True refund total (18 mo)", f"₹{h['normalized_refund_sum']/100000:.2f}L")
c2.metric("Unique tickets", f"{h['unique_tickets']:,}")
c3.metric("Q3'25 refund rate", f"{h['baseline_refund_rate']*100:.1f}%")
c4.metric("Q3'25 → 15% case", f"₹{h['potential_savings_inr_per_quarter']/100000:.1f}L/q")

st.info(
    "Data reconciliation: 12,238 source rows collapse to 11,600 unique tickets; "
    "legacy monetary values are normalized by /100 because paired legacy/helpdesk rows match exactly after conversion. "
    "The cleaned average is about ₹11.18L per quarter, consistent with the email thread's ~₹11L reference."
)

st.subheader("Executive view")
q = result["quarters"].copy()
q["Refund rate"] = q["refund_rate"] * 100
q["Refund amount (₹L)"] = q["refund_amount"] / 100000
st.line_chart(q.set_index("quarter")[["Refund rate"]])
st.dataframe(q[["quarter", "tickets", "refund_tickets", "Refund rate", "Refund amount (₹L)", "csat_mean"]].rename(columns={"quarter":"Quarter", "tickets":"Tickets", "refund_tickets":"Refund tickets", "csat_mean":"CSAT"}), use_container_width=True, hide_index=True)

st.subheader("Monthly refunds by reason")
mr = result["monthly_reason"].copy()
for col in mr.columns[1:]:
    mr[col] = mr[col].round(0)
st.dataframe(mr, use_container_width=True, hide_index=True)
st.download_button("Download monthly reason CSV", (ROOT/"outputs/monthly_refunds_by_reason.csv").read_bytes(), "monthly_refunds_by_reason.csv", "text/csv")

st.subheader("Agent view")
team_filter = st.selectbox("Team", ["All"] + sorted(result["agents"]["agent_team"].dropna().unique().tolist()))
ag = result["agents"].copy()
if team_filter != "All":
    ag = ag[ag["agent_team"] == team_filter]
ag["refund_rate"] = (ag["refund_rate"]*100).round(1)
ag["refund_amount"] = ag["refund_amount"].round(0)
ag["refund_per_ticket"] = ag["refund_per_ticket"].round(0)
ag["gw_share_of_refunds"] = (ag["gw_share_of_refunds"]*100).round(1)
st.dataframe(
    ag[["agent_id","agent_name","agent_team","agent_tier","tickets","refund_tickets","refund_amount","refund_rate","refund_per_ticket","goodwill_tickets","gw_share_of_refunds","double_awards"]],
    use_container_width=True, hide_index=True
)
st.caption("Interpret agent totals in context: Returns Desk is designed to process most refunds; Tier 2 should not be compared with Tier 1 on volume metrics per policy.")

st.subheader("Policy QA / money controls")
qa1, qa2, qa3 = st.columns(3)
qa1.metric("Refund + replacement tickets", f"{h['double_award_tickets']:,}", f"₹{h['double_award_total_exposure_inr']/100000:.2f}L exposure")
qa2.metric("Recorded GW-OTHER > ₹500", f"{h['gw_over_cap_tickets']:,}", f"₹{h['gw_over_cap_amount_inr']/100000:.2f}L tagged")
qa3.metric("AI high-confidence GW review", f"{h['ai_high_conf_gw_flags']:,}", f"₹{h['ai_high_conf_gw_amount_inr']/100000:.2f}L")

st.caption("GW-OTHER over-cap is a review signal, not automatic leakage: the code may be wrong. The AI queue suggests a standard reason for review.")

st.subheader("AI-assisted reason review queue")
gw = result["gw_flags"].copy()
show = gw[gw["ai_flag"]].copy()
show["AI confidence"] = (show["ai_confidence"]*100).round(1)
show = show[["ticket_id","agent_id","agent_name","agent_team","refund_inr","ai_suggested_reason","AI confidence","replacement_issued"]].head(100)
st.dataframe(show, use_container_width=True, hide_index=True)

st.subheader("What the data says about Q4")
st.write(
    f"Q4 2025 refund spend was ₹{h['q4_refund_amount']/100000:.2f}L vs ₹{h['q3_refund_amount']/100000:.2f}L in Q3 (+{(h['q4_refund_amount']/h['q3_refund_amount']-1)*100:.1f}%), "
    f"but the refund rate fell from {h['q3_refund_rate']*100:.1f}% to {h['q4_refund_rate']*100:.1f}% ({(h['q4_refund_rate']-h['q3_refund_rate'])*100:.1f} pp). "
    f"Average CSAT increased by only {h['q4_minus_q3_csat']:.2f} points across all responding tickets in the dataset. "
    "This supports a volume-driven spend increase more than a higher refund propensity, and the email claim of +0.4 CSAT is not reproduced by the full dataset."
)

st.subheader("Validation")
st.write(
    f"Internal consistency check: the local reason model agrees with the recorded non-GW reason code on {h['ai_standard_reason_agreement']*100:.1f}% of a held-out sample. "
    "This is label agreement, not proof that the historical dropdown code was correct. "
    f"After legacy normalization, duplicate ticket pairs had {h['duplicate_amount_mismatches']} monetary mismatches."
)
