from __future__ import annotations

from pathlib import Path
import json
import re
from typing import Dict, Tuple

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "raw"
OUT = ROOT / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

REASON_CODES = [
    "GW-OTHER", "DOA-REPL", "LOST-TRANSIT", "DUP-PAYMENT",
    "CANCEL", "PRICE-ADJ", "RETURN-QC-OK", "WTY-BUYBACK"
]


def load_data(data_dir: Path = DATA) -> Dict[str, pd.DataFrame]:
    files = {
        "tickets": data_dir / "tickets.csv",
        "agents": data_dir / "agents.csv",
        "orders": data_dir / "orders.csv",
        "customers": data_dir / "customers.csv",
        "products": data_dir / "products.csv",
    }
    missing = [str(p) for p in files.values() if not p.exists()]
    if missing:
        raise FileNotFoundError("Missing input files: " + ", ".join(missing))
    dfs = {k: pd.read_csv(v) for k, v in files.items()}
    for c in ["created_at", "first_response_at", "resolved_at"]:
        dfs["tickets"][c] = pd.to_datetime(dfs["tickets"][c], errors="coerce")
    dfs["tickets"]["refund_amount_inr"] = pd.to_numeric(
        dfs["tickets"]["refund_amount_inr"], errors="coerce"
    )
    return dfs


def clean_tickets(dfs: Dict[str, pd.DataFrame]) -> Tuple[pd.DataFrame, Dict[str, float]]:
    t = dfs["tickets"].copy()
    raw_rows = len(t)
    raw_refund_sum = float(t["refund_amount_inr"].sum())

    # The policy says legacy_fd stores money in a native unit while helpdesk stores INR.
    # The duplicate legacy/helpdesk pairs are identical on all fields except source and
    # legacy refund values are exactly 100x the helpdesk values, so /100 is used.
    t["refund_inr"] = np.where(
        t["source_system"].eq("legacy_fd"),
        t["refund_amount_inr"] / 100.0,
        t["refund_amount_inr"],
    )
    t["_source_priority"] = t["source_system"].map({"helpdesk": 0, "legacy_fd": 1}).fillna(9)
    t = t.sort_values(["ticket_id", "_source_priority"])

    duplicate_ticket_ids = int(t["ticket_id"].duplicated(keep=False).groupby(t["ticket_id"]).any().sum())
    duplicate_extra_rows = raw_rows - t["ticket_id"].nunique()

    # Keep one canonical row per ticket. Where both systems exist, prefer helpdesk.
    canonical = t.drop_duplicates("ticket_id", keep="first").copy()
    canonical.drop(columns=["_source_priority"], inplace=True)
    canonical["month"] = canonical["created_at"].dt.to_period("M").astype(str)
    canonical["quarter"] = canonical["created_at"].dt.to_period("Q").astype(str)

    # Attach agent data.
    am = dfs["agents"].set_index("agent_id")
    for col in ["name", "team", "tier", "site", "shift"]:
        canonical[f"agent_{col}"] = canonical["agent_id"].map(am[col])

    # Attach order and product reference data. Order ID + customer is the primary join.
    o = dfs["orders"].rename(columns={"sku": "order_sku", "order_value_inr": "order_value"})
    ocols = ["order_id", "customer_id", "order_sku", "qty", "order_value", "order_date", "lot_code"]
    canonical = canonical.merge(o[ocols], on=["order_id", "customer_id"], how="left")
    pcols = ["sku", "unit_cost_inr", "retail_price_inr", "warranty_months", "product_name"]
    p = dfs["products"][pcols].rename(columns={"sku": "product_sku"})
    canonical = canonical.merge(p, on="product_sku", how="left")

    canonical["refund_flag"] = canonical["refund_inr"].notna()
    canonical["double_award_flag"] = canonical["refund_flag"] & canonical["replacement_issued"].eq("Y")
    canonical["replacement_cost"] = canonical["unit_cost_inr"].fillna(0) + 340
    canonical["refund_gt_order"] = canonical["refund_flag"] & canonical["order_value"].notna() & (canonical["refund_inr"] > canonical["order_value"] + 0.01)
    canonical["goodwill_over_cap"] = canonical["refund_flag"] & canonical["refund_reason_code"].eq("GW-OTHER") & (canonical["refund_inr"] > 500)

    # Normalize duplicate check: every paired legacy/helpdesk refund must match after /100.
    t2 = t.sort_values(["ticket_id", "_source_priority"])
    paired = t2[t2["ticket_id"].duplicated(False)].groupby("ticket_id")["refund_inr"].agg(lambda s: sorted(s.dropna().unique()))
    duplicate_amount_mismatches = int(sum(len(v) > 1 for v in paired))

    meta = {
        "raw_rows": raw_rows,
        "unique_tickets": int(canonical["ticket_id"].nunique()),
        "duplicate_ticket_ids": duplicate_ticket_ids,
        "duplicate_extra_rows": duplicate_extra_rows,
        "raw_refund_sum": raw_refund_sum,
        "normalized_refund_sum": float(canonical["refund_inr"].sum()),
        "normalized_refund_tickets": int(canonical["refund_flag"].sum()),
        "duplicate_amount_mismatches": duplicate_amount_mismatches,
    }
    return canonical, meta


def monthly_reason_table(c: pd.DataFrame) -> pd.DataFrame:
    x = c[c["refund_flag"]].pivot_table(
        index="month", columns="refund_reason_code", values="refund_inr", aggfunc="sum", fill_value=0
    )
    return x.reindex(columns=[k for k in REASON_CODES if k in x.columns], fill_value=0).reset_index()


def monthly_agent_table(c: pd.DataFrame) -> pd.DataFrame:
    return (
        c[c["refund_flag"]]
        .groupby(["month", "agent_id", "agent_name", "agent_team"], as_index=False)
        .agg(refund_tickets=("ticket_id", "count"), refund_amount=("refund_inr", "sum"))
        .sort_values(["month", "refund_amount"], ascending=[True, False])
    )


def agent_table(c: pd.DataFrame) -> pd.DataFrame:
    g = c.groupby(["agent_id", "agent_name", "agent_team", "agent_tier"], dropna=False)
    x = g.agg(
        tickets=("ticket_id", "size"),
        refund_tickets=("refund_flag", "sum"),
        refund_amount=("refund_inr", "sum"),
        goodwill_tickets=("refund_reason_code", lambda s: int((s == "GW-OTHER").sum())),
        goodwill_amount=("refund_inr", lambda s: float(s.where(c.loc[s.index, "refund_reason_code"] == "GW-OTHER").sum())),
        double_awards=("double_award_flag", "sum"),
    ).reset_index()
    x["refund_rate"] = x["refund_tickets"] / x["tickets"]
    x["refund_per_ticket"] = x["refund_amount"] / x["tickets"]
    x["gw_share_of_refunds"] = np.where(x["refund_tickets"] > 0, x["goodwill_tickets"] / x["refund_tickets"], np.nan)
    return x.sort_values("refund_amount", ascending=False)


def team_table(c: pd.DataFrame) -> pd.DataFrame:
    g = c.groupby(["agent_team", "agent_tier"], dropna=False)
    x = g.agg(
        tickets=("ticket_id", "size"),
        refund_tickets=("refund_flag", "sum"),
        refund_amount=("refund_inr", "sum"),
        goodwill_tickets=("refund_reason_code", lambda s: int((s == "GW-OTHER").sum())),
        double_awards=("double_award_flag", "sum"),
    ).reset_index()
    x["refund_rate"] = x["refund_tickets"] / x["tickets"]
    x["refund_per_ticket"] = x["refund_amount"] / x["tickets"]
    return x.sort_values("refund_amount", ascending=False)


def quarter_table(c: pd.DataFrame) -> pd.DataFrame:
    g = c.groupby("quarter")
    x = g.agg(
        tickets=("ticket_id", "size"),
        refund_tickets=("refund_flag", "sum"),
        refund_amount=("refund_inr", "sum"),
        csat_mean=("csat_score", "mean"),
        csat_responses=("csat_score", lambda s: int(s.notna().sum())),
    ).reset_index()
    x["refund_rate"] = x["refund_tickets"] / x["tickets"]
    return x


def train_reason_assistant(c: pd.DataFrame):
    r = c[c["refund_flag"] & c["refund_reason_code"].notna()].copy()
    r["text"] = r["customer_message"].fillna("") + " " + r["agent_notes"].fillna("")
    standard = r[r["refund_reason_code"] != "GW-OTHER"].copy()
    Xtr, Xte, ytr, yte = train_test_split(
        standard["text"], standard["refund_reason_code"],
        test_size=0.25, random_state=42, stratify=standard["refund_reason_code"]
    )
    model = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)),
        ("clf", LogisticRegression(max_iter=2000, class_weight="balanced")),
    ])
    model.fit(Xtr, ytr)
    accuracy = float(accuracy_score(yte, model.predict(Xte)))

    gw = r[r["refund_reason_code"] == "GW-OTHER"].copy()
    if len(gw):
        probs = model.predict_proba(gw["text"])
        idx = probs.argmax(axis=1)
        gw["ai_suggested_reason"] = model.classes_[idx]
        gw["ai_confidence"] = probs.max(axis=1)
        gw["ai_flag"] = gw["ai_confidence"] >= 0.80
    else:
        gw["ai_suggested_reason"] = []
        gw["ai_confidence"] = []
        gw["ai_flag"] = []
    return model, accuracy, gw


def run_analysis(data_dir: Path = DATA) -> Dict[str, object]:
    dfs = load_data(data_dir)
    c, meta = clean_tickets(dfs)
    monthly_reason = monthly_reason_table(c)
    monthly_agent = monthly_agent_table(c)
    agents = agent_table(c)
    teams = team_table(c)
    quarters = quarter_table(c)
    model, model_agreement, gw_flags = train_reason_assistant(c)

    q3 = quarters.loc[quarters["quarter"] == "2025Q3"].iloc[0]
    avg_refund = float(c.loc[c["refund_flag"], "refund_inr"].mean())
    quarterly_tickets_at_volume = 650 * 13
    target_rate = 0.15
    baseline_rate = float(q3["refund_rate"])
    potential_savings = max(0.0, baseline_rate - target_rate) * quarterly_tickets_at_volume * avg_refund

    double = c[c["double_award_flag"]]
    q4 = quarters.loc[quarters["quarter"] == "2025Q4"].iloc[0]
    csat_delta = float(q4["csat_mean"] - q3["csat_mean"])

    headline = {
        **meta,
        "baseline_quarter": "2025Q3",
        "baseline_refund_rate": baseline_rate,
        "target_refund_rate": target_rate,
        "avg_refund_inr": avg_refund,
        "vireo_weekly_tickets_assumption": 650,
        "quarterly_ticket_assumption": quarterly_tickets_at_volume,
        "potential_savings_inr_per_quarter": potential_savings,
        "double_award_tickets": int(len(double)),
        "double_award_refund_inr": float(double["refund_inr"].sum()),
        "double_award_replacement_cost_inr": float(double["replacement_cost"].sum()),
        "double_award_total_exposure_inr": float((double["refund_inr"] + double["replacement_cost"]).sum()),
        "gw_over_cap_tickets": int(c["goodwill_over_cap"].sum()),
        "gw_over_cap_amount_inr": float(c.loc[c["goodwill_over_cap"], "refund_inr"].sum()),
        "ai_standard_reason_agreement": model_agreement,
        "ai_high_conf_gw_flags": int(gw_flags["ai_flag"].sum()),
        "ai_high_conf_gw_amount_inr": float(gw_flags.loc[gw_flags["ai_flag"], "refund_inr"].sum()),
        "q3_refund_amount": float(q3["refund_amount"]),
        "q4_refund_amount": float(q4["refund_amount"]),
        "q3_refund_rate": float(q3["refund_rate"]),
        "q4_refund_rate": float(q4["refund_rate"]),
        "q3_csat": float(q3["csat_mean"]),
        "q4_csat": float(q4["csat_mean"]),
        "q4_minus_q3_csat": csat_delta,
    }

    # Write CSVs for board-pack use.
    monthly_reason.to_csv(OUT / "monthly_refunds_by_reason.csv", index=False)
    monthly_agent.to_csv(OUT / "monthly_refunds_by_agent.csv", index=False)
    agents.to_csv(OUT / "agent_refund_summary.csv", index=False)
    teams.to_csv(OUT / "team_refund_summary.csv", index=False)
    quarters.to_csv(OUT / "quarter_summary.csv", index=False)
    gw_flags.sort_values("ai_confidence", ascending=False).to_csv(OUT / "ai_gw_review_queue.csv", index=False)
    pd.DataFrame([headline]).to_csv(OUT / "headline_metrics.csv", index=False)
    (OUT / "headline_metrics.json").write_text(json.dumps(headline, indent=2), encoding="utf-8")

    return {
        "data": c,
        "headline": headline,
        "monthly_reason": monthly_reason,
        "monthly_agent": monthly_agent,
        "agents": agents,
        "teams": teams,
        "quarters": quarters,
        "gw_flags": gw_flags,
        "model_agreement": model_agreement,
        "model": model,
    }


if __name__ == "__main__":
    result = run_analysis()
    h = result["headline"]
    print(json.dumps({k: h[k] for k in [
        "raw_rows", "unique_tickets", "duplicate_ticket_ids", "raw_refund_sum",
        "normalized_refund_sum", "baseline_refund_rate", "potential_savings_inr_per_quarter",
        "double_award_tickets", "double_award_total_exposure_inr", "ai_high_conf_gw_flags",
        "ai_high_conf_gw_amount_inr", "ai_standard_reason_agreement"
    ]}, indent=2))
