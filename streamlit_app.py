"""Uwazi Trace: evidence-first review of public procurement data (Streamlit front end)."""
from __future__ import annotations

import os
import sys
import tempfile
import uuid
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from uwazi import __version__  # noqa: E402
from uwazi.alerts import TIER_MEANING  # noqa: E402
from uwazi.audit import OUTCOMES, AuditLog  # noqa: E402
from uwazi.cleaning import completeness  # noqa: E402
from uwazi.config import Settings  # noqa: E402
from uwazi.indicators import INDICATORS  # noqa: E402
from uwazi.pipeline import run  # noqa: E402
from uwazi.schema import REQUIRED_COLUMNS, template_csv  # noqa: E402
from uwazi.synthetic import generate  # noqa: E402
from uwazi.ui import components as ui  # noqa: E402
from uwazi.ui.theme import css  # noqa: E402

FEEDBACK_URL = os.environ.get("FEEDBACK_URL", "")
st.set_page_config(page_title="Uwazi Trace", page_icon="🔎", layout="wide", initial_sidebar_state="collapsed")
st.markdown(css(), unsafe_allow_html=True)
st.markdown(ui.kanga_strip(), unsafe_allow_html=True)
if st.session_state.pop("flash", None):
    st.toast("Review saved to the activity log", icon="✅")


# ------------------------------------------------------------------ data
@st.cache_data(show_spinner=False)
def load_synthetic() -> pd.DataFrame:
    return generate()


@st.cache_data(show_spinner="Looking for patterns…")
def analyse(raw: pd.DataFrame, settings: dict):
    return run(raw, Settings(**settings))


def get_audit() -> AuditLog:
    if "audit_path" not in st.session_state:   # one private log per visitor session
        st.session_state.audit_path = os.path.join(tempfile.gettempdir(), f"uwazi_{uuid.uuid4().hex}.db")
    return AuditLog(st.session_state.audit_path)


# --------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown("### Data and settings")
    source = st.radio("Data source", ["Synthetic demo", "Upload CSV"], label_visibility="collapsed")
    upload = None
    if source == "Upload CSV":
        st.warning("Public demo: please do not upload real, confidential or personal data.")
        upload = st.file_uploader("Awards CSV", type="csv")
        st.download_button("Download CSV template", template_csv(), "uwazi_template.csv")
    with st.expander("Assumptions you control"):
        threshold = st.number_input("Approval threshold (KES)", value=5_000_000, step=500_000, min_value=1)
        window = st.number_input("Minimum bid window (days)", value=14, min_value=0)
        floor = st.number_input("Materiality floor (KES)", value=1_000_000, step=500_000, min_value=0)
        alpha = st.slider("Price sensitivity (alpha)", 0.005, 0.10, 0.02, 0.005, help="Lower means fewer price flags.")
        inflation = st.number_input("Annual price inflation (%)", value=0.0, step=1.0) / 100
        fuzzy = st.checkbox("Merge near-identical supplier names", value=True, help="Every merge is listed on the Today tab.")
        st.caption("Thresholds and windows are assumptions. Check them against current procurement Regulations.")
    reviewer = st.text_input("Your reviewer ID", "reviewer-1", max_chars=40)
    if FEEDBACK_URL:
        st.link_button("Send feedback", FEEDBACK_URL)

st.markdown(ui.brand("Synthetic demo data" if source == "Synthetic demo" else "Your uploaded data"), unsafe_allow_html=True)

if source == "Upload CSV":
    if upload is None:
        st.info("Upload a CSV with these columns: " + ", ".join(REQUIRED_COLUMNS))
        st.stop()
    raw = pd.read_csv(upload)
else:
    raw = load_synthetic()

settings = Settings(approval_threshold_kes=float(threshold), min_bid_window_days=int(window), materiality_floor_kes=float(floor),
                    price_alpha=float(alpha), annual_inflation=float(inflation), fuzzy_supplier_merge=bool(fuzzy))
try:
    result = analyse(raw, asdict(settings))
except ValueError as err:
    st.error(str(err))
    st.stop()
audit = get_audit()
reviews = audit.latest_reviews()
awards, alerts, signals = result.awards, result.alerts, result.signals


# ---------------------------------------------------------------- dialog
@st.dialog("Award review", width="large")
def award_dialog(award_id: str) -> None:
    a = next(alerts[alerts.award_id == award_id].itertuples())
    st.markdown(ui.award_summary(a), unsafe_allow_html=True)
    for s in signals[signals.award_id == award_id].itertuples():
        st.markdown(ui.finding_card(s.indicator, s.detail, s.baseline), unsafe_allow_html=True)
    trail = [e for e in audit.entries(1000) if e["obj"] == award_id]
    source_line = (f'<a href="{ui.E(a.source_url)}" target="_blank" rel="noopener">{ui.E(a.source_url)}</a>'
                   if str(a.source_url).startswith("http") and "example.invalid" not in str(a.source_url) else ui.E(a.source_url))
    st.markdown(
        '<div class="card"><div class="lbl" style="margin-top:0">4 · Confidence and uncertainty</div>'
        f'<div>Evidence grade <b>{a.evidence_grade}</b>{" (all key fields present)" if a.evidence_grade == "A" else " (some fields missing: " + ui.E(a.dq) + ")"}. '
        'Baselines are empirical and limited to the peer cohort, specifications are not modelled, and settings are assumptions. '
        'A flag is a prompt to check, not a finding.</div>'
        f'<div class="lbl">6 · Source documents</div><div class="mono">{source_line}</div>'
        '<div class="mono">A production system stores the archived page with its SHA-256 and page references.</div>'
        f'<div class="lbl">7 · Audit trail</div><div>{len(trail)} recorded {"entry" if len(trail) == 1 else "entries"} for this award.</div></div>',
        unsafe_allow_html=True)
    st.markdown("#### Record your review")
    outcome = st.radio("Outcome", list(OUTCOMES), format_func=OUTCOMES.get, horizontal=True, key=f"o_{award_id}")
    code = st.text_input("Explanation code (optional)", placeholder="for example special_spec", max_chars=60, key=f"c_{award_id}")
    notes = st.text_area("Notes", placeholder="What you checked and what you found", max_chars=500, key=f"n_{award_id}")
    if st.button("Save review", type="primary", key=f"s_{award_id}"):
        audit.record_review(award_id, reviewer, outcome, code.strip(), notes.strip())
        st.session_state["flash"] = True
        st.rerun()


def rows(df: pd.DataFrame, prefix: str, limit: int = 25) -> None:
    for a in list(df.head(limit).itertuples()):
        left, right = st.columns([5, 1.2], vertical_alignment="center")
        left.markdown(ui.alert_row(a, reviews.get(a.award_id, {}).get("outcome")), unsafe_allow_html=True)
        if right.button("Open", key=f"{prefix}_{a.award_id}"):
            award_dialog(a.award_id)
    if len(df) > limit:
        st.caption(f"Showing the first {limit} of {len(df)}. Use the filters to narrow the list.")


# ----------------------------------------------------------------- pages
tab_today, tab_review, tab_insights, tab_activity, tab_about = st.tabs(["Today", "Review", "Insights", "Activity", "About and method"])

with tab_today:
    tiers = alerts["tier"].value_counts().to_dict()
    monthly = awards.groupby(awards["award_date"].dt.to_period("M"))["award_value_kes"].sum().sort_index().tolist()
    st.markdown('<div class="hello">Habari. Here is what deserves <em>a second look</em> today.</div>'
                '<p class="lead">Flags show where spending looks unusual compared with similar purchases elsewhere. '
                'They are questions for a person to ask, never conclusions.</p>', unsafe_allow_html=True)
    st.markdown(ui.hero(awards.award_value_kes.sum(), len(awards), float(awards.bidder_count.isna().mean()), tiers, monthly), unsafe_allow_html=True)
    left, right = st.columns([1.15, 1])
    with left:
        with st.container(key="card_today"):
            st.markdown('<div class="hd">Worth a closer look</div><div class="sub">The strongest cases first. Open one to see the evidence.</div>', unsafe_allow_html=True)
            rows(alerts, "today", limit=5)
    with right:
        by_cat = awards.groupby("category")["award_value_kes"].sum().sort_values(ascending=False)
        st.markdown('<div class="card"><h3>Where the money goes</h3><p class="sub">Share of award value by category.</p>'
                    + ui.donut(list(by_cat.items())) + "</div>", unsafe_allow_html=True)
        comp = "".join(ui.bar(k, "", v) for k, v in completeness(awards).items())
        st.markdown(f'<div class="card"><h3>How complete is the data?</h3><p class="sub">Flags are only as good as the records behind them.</p>{comp}</div>', unsafe_allow_html=True)
    counts = signals.groupby("indicator")["award_id"].nunique() if len(signals) else pd.Series(dtype=int)
    colors = ["#c23566", "#1e8c82", "#d9931a", "#7a3b8f", "#e4577f"]
    minis = "".join(f'<div class="mini"><i style="background:{colors[i]}"></i><b>{int(counts.get(code, 0))}</b><span>{ui.E(ind.name)}</span></div>'
                    for i, (code, ind) in enumerate(INDICATORS.items()))
    st.markdown(f'<div class="gh"><b>Signals at a glance</b><span>Awards touched by each kind of signal</span></div><div class="grid">{minis}</div>', unsafe_allow_html=True)
    if len(result.merges):
        with st.expander(f"Supplier name matching: {len(result.merges)} name variants merged"):
            st.caption("Every merge is listed, and the original name is kept. A wrong merge is worse than a missed one, so names with different numbers never merge.")
            st.dataframe(result.merges, hide_index=True, width="stretch")
    with st.expander("What this view cannot see"):
        st.write("Payments below the publication threshold, awards that were never posted, company ownership, project delivery, and any document that is not in the dataset. "
                 "A quiet queue is not a clean bill of health.")

with tab_review:
    st.markdown('<div class="hello">The <em>review</em> queue</div><p class="lead">Tier shows how many independent kinds of signal fired. '
                'It is a priority for a human to look, never a verdict.</p>', unsafe_allow_html=True)
    f1, f2, f3 = st.columns([1.3, 1, 1])
    tier_pick = f1.pills("Priority", ["All", "Tier 1", "Tier 2", "Tier 3"], default="All", label_visibility="collapsed") or "All"
    entity = f2.selectbox("Entity", ["All entities", *sorted(alerts.entity.unique())], label_visibility="collapsed")
    signal_name = f3.selectbox("Signal", ["All signals", *[i.name for i in INDICATORS.values()]], label_visibility="collapsed")
    query = st.text_input("Search supplier", placeholder="Search by supplier name", label_visibility="collapsed")
    view = alerts
    if tier_pick != "All":
        view = view[view.tier == int(tier_pick[-1])]
    if entity != "All entities":
        view = view[view.entity == entity]
    if signal_name != "All signals":
        code = next(c for c, i in INDICATORS.items() if i.name == signal_name)
        view = view[view.indicators.map(lambda x: code in x)]
    if query:
        view = view[view.supplier.str.contains(query, case=False, regex=False)]
    if view.empty:
        st.markdown('<div class="card">Nothing matches these filters.</div>', unsafe_allow_html=True)
    for t in (1, 2, 3):
        part = view[view.tier == t]
        if part.empty:
            continue
        with st.container(key=f"card_t{t}"):
            st.markdown(f'<div class="hd">Tier {t}</div><div class="sub">{TIER_MEANING[t]} · {len(part)}</div>', unsafe_allow_html=True)
            rows(part, f"rev{t}")

with tab_insights:
    st.markdown('<div class="hello">How does one entity <em>compare</em>?</div><p class="lead">Each entity is set against peers buying the same category. '
                'This is context for reviewers, not a league table.</p>', unsafe_allow_html=True)
    ents = sorted(awards.entity.unique())
    pick = st.selectbox("Entity", ents, index=ents.index("County A Health") if "County A Health" in ents else 0, label_visibility="collapsed")
    conc = result.concentration[(result.concentration.entity == pick) & (result.concentration.n >= settings.min_cohort_awards)]
    meth = result.method[(result.method.entity == pick) & (result.method.n >= settings.min_cohort_awards)]
    a1 = "".join(ui.bar(r.category, f"FY{r.fy} · {r.n} awards", r.share, r.peer_median, r.peer_p90) for r in conc.itertuples())
    a2 = "".join(ui.bar(r.category, f"FY{r.fy} · {r.n} awards", r.share, r.peer_median, r.peer_p90) for r in meth.itertuples())
    empty = '<p class="sub">Fewer than 5 awards in each category and year.</p>'
    st.markdown('<div class="card"><h3>Share of value taken by the top supplier</h3><p class="sub">Dark tick: peer median. Faint tick: peer 90th percentile.</p>' + (a1 or empty) + "</div>", unsafe_allow_html=True)
    st.markdown('<div class="card"><h3>Share awarded without open competition</h3><p class="sub">Direct, restricted and emergency awards, by value.</p>' + (a2 or empty) + "</div>", unsafe_allow_html=True)
    T = settings.approval_threshold_kes
    vals = awards.loc[awards.entity == pick, "award_value_kes"]
    edges = [0.5 * T + i * T / 20 for i in range(21)]
    counts_h = [int(((vals >= edges[i]) & (vals < edges[i + 1])).sum()) for i in range(20)]
    st.markdown(f'<div class="card"><h3>Award values near the approval threshold</h3><p class="sub">From 50% to 150% of KES {T:,.0f}. '
                'Dark bars sit just under it. A sharp step at the threshold is what the bunching test looks for.</p>' + ui.histogram(counts_h, range(8, 10)) + "</div>", unsafe_allow_html=True)
    with st.expander("Awards observed by entity and fiscal year (coverage)"):
        st.caption("Low counts usually mean incomplete publication, not low spending.")
        st.dataframe(awards.pivot_table(index="entity", columns="fy", values="award_id", aggfunc="count", fill_value=0), width="stretch")

with tab_activity:
    st.markdown('<div class="hello">Every decision, <em>on the record</em></div><p class="lead">Reviews are stored with a SHA-256 hash that includes the previous entry, '
                'so editing the past breaks the chain. Your log is private to this browser session.</p>', unsafe_allow_html=True)
    b1, b2, b3, _ = st.columns([1, 1.3, 0.8, 3])
    verdict = None
    if b1.button("Verify chain", type="primary"):
        verdict = audit.verify()
    if b2.button("Demonstrate tampering"):
        if audit.tamper_for_demo():
            verdict = audit.verify()
        else:
            st.info("Record a review first, then try again.")
    if b3.button("Reset"):
        audit.reset()
        st.rerun()
    if verdict is True:
        st.markdown('<p class="ok">Chain intact: no entry has been altered.</p>', unsafe_allow_html=True)
    elif verdict is False:
        st.markdown('<p class="bad">Chain broken: an entry was altered after it was recorded.</p>', unsafe_allow_html=True)
    entries = audit.entries()
    st.markdown('<div class="card">' + (ui.timeline_html(entries) if entries else
                '<p class="sub">No reviews yet. Open an award from the Review tab and record an outcome.</p>') + "</div>", unsafe_allow_html=True)

with tab_about:
    st.markdown('<div class="hello">What this is, and <em>what it is not</em></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="card"><h3>An evidence-first review tool</h3><p>Uwazi Trace finds awards that look unusual <b>compared with peers</b>, shows the evidence and the baseline, '
        'lists the innocent explanations, and records what a human decided. It exists to point scarce review time in the right direction.</p>'
        '<h3 style="margin-top:14px">What it is not</h3><p>It is not a corruption detector. It never scores a person, a politician or a company. A flag is a question, not a finding, '
        'and a quiet queue does not mean clean books.</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="gh"><b>The five signals</b><span>Each one compares like with like and needs enough comparators</span></div>', unsafe_allow_html=True)
    for ind in INDICATORS.values():
        st.markdown(f'<div class="card"><h3>{ui.E(ind.name)}<span class="fam">{ui.E(ind.family)}</span></h3><p>{ui.E(ind.question)}</p>'
                    f'<div class="lbl">Innocent explanations to check first</div>{ui.tags(ind.legitimate)}</div>', unsafe_allow_html=True)
    if source == "Synthetic demo" and "planted" in raw.columns:
        mapping = {"conc": "CONC", "split": "THRESH", "bunch": "THRESH", "price": "PRICE", "short": "TIMELINE"}
        labels = {"conc": "Supplier concentration", "split": "Splitting", "bunch": "Bunching below threshold", "price": "Inflated unit prices", "short": "Very short bid windows"}
        bench = []
        for key, code in mapping.items():
            planted = set(raw.loc[raw.planted == key, "award_id"])
            found = set(signals.loc[signals.indicator == code, "award_id"]) if len(signals) else set()
            bench.append({"Planted pattern": labels[key], "Planted": len(planted), "Found": len(planted & found), "Recall": len(planted & found) / len(planted)})
        with st.expander("How well does it work on the synthetic benchmark?"):
            st.dataframe(pd.DataFrame(bench), hide_index=True, column_config={"Recall": st.column_config.ProgressColumn(format="percent", min_value=0, max_value=1)}, width="stretch")
            st.caption("Synthetic data is clean and random, so real-world precision will be lower. Detectors are deliberately conservative for prices. "
                       "Real validation needs blind review by auditors and procurement practitioners (see docs/VALIDATION.md).")
    with st.expander("Data, privacy and limits"):
        st.write("This public demo uses fully synthetic records. Do not upload real or personal data. Your reviews live only in your browser session. "
                 "Before real data is used, a Kenyan lawyer should review defamation and Data Protection Act risks, a right-of-reply step should exist, and source terms should be checked.")
    with st.expander("Version"):
        st.write(f"Uwazi Trace {__version__} · prototype · MIT licensed · fonts Fraunces and DM Sans (SIL Open Font License)")

st.markdown(ui.proverb(), unsafe_allow_html=True)
