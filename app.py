"""
app.py — Streamlit UI for EliseAI Lead Enrichment Agent
Run with: python -m streamlit run app.py
"""

import json
import pandas as pd
import streamlit as st
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from agent import enrich_lead

# ── Page config ────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="EliseAI Lead Enrichment",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Styling ────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  .tier-badge {
    display: inline-block;
    padding: 6px 20px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 16px;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
  }
  .tier-A { background: #064e3b; color: #d1fae5; }
  .tier-B { background: #78350f; color: #fef3c7; }
  .tier-C { background: #7f1d1d; color: #fee2e2; }

  .metric-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 16px;
    text-align: center;
    margin-bottom: 8px;
  }
  .metric-num { font-size: 26px; font-weight: 700; color: #f1f5f9; }
  .metric-label { font-size: 11px; color: #94a3b8; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.5px; }
  .metric-source { font-size: 10px; color: #475569; margin-top: 2px; }

  .talking-point {
    background: #0f172a;
    border-left: 3px solid #38bdf8;
    padding: 10px 14px;
    border-radius: 0 8px 8px 0;
    margin-bottom: 8px;
    font-size: 14px;
    color: #e2e8f0;
    line-height: 1.5;
  }

  .time-saved-banner {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    color: white;
    padding: 10px 18px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 500;
    display: inline-block;
    margin: 8px 0 16px 0;
  }

  .email-box {
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 18px;
    font-size: 14px;
    white-space: pre-wrap;
    font-family: 'Inter', sans-serif;
    line-height: 1.7;
    color: #e2e8f0;
  }

  .section-header {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #94a3b8;
    margin-bottom: 8px;
  }

  .scheduler-pill {
    background: #052e16;
    border: 1px solid #166534;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 12px;
    color: #86efac;
    display: inline-block;
  }

  .rationale-box {
    background: #0f172a;
    border-left: 3px solid #6366f1;
    padding: 12px 16px;
    border-radius: 0 8px 8px 0;
    font-size: 15px;
    color: #cbd5e1;
    line-height: 1.6;
    margin: 10px 0 16px 0;
  }
</style>
""", unsafe_allow_html=True)


# ── Scheduler ─────────────────────────────────────────────────────────────────

def _process_scheduled_leads():
    import os
    try:
        df = pd.read_csv("sample_leads.csv")
        results = st.session_state.get("scheduled_results", {})
        for _, row in df.iterrows():
            lead_key = f"{row['company']}_{row['city']}"
            if lead_key not in results:
                results[lead_key] = enrich_lead(row.to_dict())
        st.session_state["scheduled_results"] = results
        st.session_state["last_scheduled_run"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    except Exception as e:
        st.session_state["scheduler_error"] = str(e)


def _start_scheduler():
    if st.session_state.get("_scheduler_started"):
        return
    scheduler = BackgroundScheduler()
    scheduler.add_job(_process_scheduled_leads, trigger="cron", hour=9, minute=0)
    scheduler.start()
    st.session_state["_scheduler_started"] = True
    st.session_state["_scheduler"] = scheduler


_start_scheduler()


# ── Result renderer ────────────────────────────────────────────────────────────

def render_result(result: dict, lead_name: str = ""):
    if "error" in result and "tier" not in result:
        st.error(f"❌ Agent error: {result['error']}")
        if "raw" in result:
            with st.expander("Raw response"):
                st.code(result["raw"])
        return

    tier = result.get("tier", "?")
    tier_labels = {"A": "🟢 Tier A — Priority Outreach", "B": "🟡 Tier B — Nurture", "C": "🔴 Tier C — Low Priority"}
    tier_classes = {"A": "tier-A", "B": "tier-B", "C": "tier-C"}

    # Tier badge
    st.markdown(
        f'<span class="tier-badge {tier_classes.get(tier, "")}">'
        f'{tier_labels.get(tier, f"Tier {tier}")}</span>',
        unsafe_allow_html=True,
    )

    # Rationale
    st.markdown(
        f'<div class="rationale-box">{result.get("score_rationale", "")}</div>',
        unsafe_allow_html=True,
    )

    # Dense Sales Signal
    signal = result.get("sales_signal")
    if signal:
        st.markdown(
            f'<div style="background: #1e293b; border: 1px solid #475569; padding: 10px; border-radius: 8px; font-family: monospace; font-size: 13px; color: #34d399; margin-bottom: 16px;">'
            f'<strong>⚡ OPTIMIZED SIGNAL:</strong> {signal}</div>',
            unsafe_allow_html=True
        )

    # Time saved
    minutes = result.get("estimated_time_saved_minutes")
    if minutes:
        st.markdown(
            f'<div class="time-saved-banner">⏱ ~{minutes} min saved vs. manual research</div>',
            unsafe_allow_html=True,
        )

    st.divider()

    # ── Key metrics (all from real APIs) ──────────────────────────────────────
    kd = result.get("key_data_points", {})
    raw = result.get("_raw_data", {})
    census = raw.get("census", {})
    fred = raw.get("fred", {})

    def metric_card(col, val, label, source, suffix=""):
        with col:
            display = f"{val}{suffix}" if val is not None else "N/A"
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="metric-num">{display}</div>'
                f'<div class="metric-label">{label}</div>'
                f'<div class="metric-source">{source}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    c1, c2, c3, c4 = st.columns(4)
    metric_card(c1, kd.get("renter_pct"), "Renter %", "US Census ACS", "%")
    metric_card(c2, kd.get("vacancy_rate"), "Vacancy Rate", "US Census ACS", "%")
    metric_card(c3, kd.get("rent_growth_pct"), "Rent Growth YoY", "St. Louis Fed", "%")
    metric_card(c4, kd.get("median_income") and f"${kd.get('median_income'):,}", "Median Income", "US Census ACS")

    st.markdown("<br>", unsafe_allow_html=True)

    col_l, col_r = st.columns([1, 1])

    with col_l:
        st.markdown('<div class="section-header">💬 SDR Talking Points</div>', unsafe_allow_html=True)
        for tp in result.get("talking_points", []):
            st.markdown(f'<div class="talking-point">{tp}</div>', unsafe_allow_html=True)

        # Buying Signals
        signals = result.get("buying_signals", {})
        if signals:
            st.markdown('<div class="section-header" style="margin-top:16px">🔔 Buying Signals</div>', unsafe_allow_html=True)
            signal_detected = False
            for sig_name, sig_value in signals.items():
                if sig_value and sig_value not in [False, None]:
                    signal_detected = True
                    sig_label = sig_name.replace("_", " ").title()
                    st.success(f"**{sig_label}:** {sig_value}")
            if not signal_detected:
                st.info("No active buying signals detected")
        
        # Objection Handling
        objections = result.get("objection_handling", {})
        if objections:
            st.markdown('<div class="section-header" style="margin-top:16px">🎯 Objection Handling</div>', unsafe_allow_html=True)
            with st.expander("View pre-built responses to common objections"):
                for obj_name, obj_response in objections.items():
                    if obj_response:
                        st.markdown(f"**{obj_name.replace('_', ' ').title()}:** {obj_response}")

        top_news = kd.get("top_news_headline")
        if top_news:
            st.markdown('<div class="section-header" style="margin-top:16px">📰 Most Recent Signal</div>', unsafe_allow_html=True)
            st.info(top_news)

    with col_r:
        st.markdown('<div class="section-header">✉️ Draft Outreach Email</div>', unsafe_allow_html=True)
        email = result.get("email_draft", {})
        if isinstance(email, dict):
            email_body = email.get("body", "")
            email_subject = email.get("subject", "")
        else:
            email_body = str(email)
            email_subject = ""
        
        if email_body:
            display_email = f"Subject: {email_subject}\n\n{email_body}" if email_subject else email_body
            st.markdown(f'<div class="email-box">{display_email}</div>', unsafe_allow_html=True)
            st.download_button(
                label="📋 Download Email (.txt)",
                data=display_email,
                file_name=f"email_{lead_name.replace(' ', '_').lower()}.txt",
                mime="text/plain",
                use_container_width=True,
            )
        else:
            st.info("No email draft generated")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Raw API Data Inspector ─────────────────────────────────────────────────
    with st.expander("🔍 Inspect Raw API Data"):
        tab1, tab2, tab3 = st.tabs(["Census", "FRED", "News"])
        with tab1:
            if census:
                st.json(census)
            else:
                st.warning("No Census data returned.")
        with tab2:
            if fred:
                st.json(fred)
            else:
                st.warning("No FRED data returned.")
        with tab3:
            news = raw.get("news", {})
            if news:
                st.json(news)
            else:
                st.warning("No News data returned.")


# ── Header ────────────────────────────────────────────────────────────────────

st.markdown("## 🏢 EliseAI Lead Enrichment Agent")
st.markdown(
    "Researches and scores inbound leads using **live Census data**, **FRED rent trends**, "
    "and **company news** — then drafts personalized, grounded SDR outreach in seconds."
)

last_run = st.session_state.get("last_scheduled_run")
if last_run:
    st.markdown(f'<span class="scheduler-pill">🕘 Last scheduled run: {last_run}</span>', unsafe_allow_html=True)
else:
    st.markdown('<span class="scheduler-pill">🕘 Scheduler active — runs daily at 9am</span>', unsafe_allow_html=True)

st.divider()


# ── Tabs ──────────────────────────────────────────────────────────────────────

tab_single, tab_batch = st.tabs(["🔍 Enrich a Lead", "📋 Batch Upload"])


# ── Tab 1: Single lead ────────────────────────────────────────────────────────

with tab_single:
    st.markdown("### Enter Lead Details")
    col1, col2 = st.columns(2)
    with col1:
        name     = st.text_input("Contact Name", placeholder="Sarah Chen", key="s_name")
        email_in = st.text_input("Email Address", placeholder="s.chen@greystar.com", key="s_email")
        company  = st.text_input("Company", placeholder="Greystar", key="s_company")
    with col2:
        address  = st.text_input("Property Address", placeholder="450 W 33rd St", key="s_address")
        city     = st.text_input("City", placeholder="Austin", key="s_city")
        state    = st.text_input("State (2-letter)", placeholder="TX", max_chars=2, key="s_state")

    run_btn = st.button("✨ Enrich Lead", type="primary", use_container_width=True, key="run_single")

    if run_btn:
        if not all([name, company, address, city, state]):
            st.warning("Please fill in all fields before enriching.")
        else:
            lead = {
                "name": name, "email": email_in, "company": company,
                "property_address": address, "city": city, "state": state.upper(),
            }

            progress_text = st.empty()
            progress_bar  = st.progress(0)
            steps = ["Fetching Census data...", "Fetching FRED rent data...",
                     "Fetching company news...", "Reasoning with Groq..."]
            step_idx = [0]

            def update_progress(status: str):
                pct = min(step_idx[0] / len(steps), 0.92)
                progress_bar.progress(pct)
                progress_text.markdown(f"*{status}*")
                step_idx[0] += 1

            with st.spinner(""):
                result = enrich_lead(lead, progress_callback=update_progress)

            progress_bar.progress(1.0)
            progress_text.empty()
            progress_bar.empty()

            st.success("✅ Lead enriched with live data.")
            st.divider()
            render_result(result, lead_name=name)

            if "single_results" not in st.session_state:
                st.session_state["single_results"] = {}
            st.session_state["single_results"][f"{company}_{city}"] = result


# ── Tab 2: Batch upload ───────────────────────────────────────────────────────

with tab_batch:
    st.markdown("### Upload a Lead List (CSV)")
    st.markdown("CSV must have columns: `name`, `email`, `company`, `property_address`, `city`, `state`")

    import os as _os
    sample_df = pd.read_csv("leads.csv") if _os.path.exists("leads.csv") else None
    if sample_df is not None:
        st.download_button("📥 Download leads.csv", data=sample_df.to_csv(index=False),
                           file_name="leads.csv", mime="text/csv")

    uploaded = st.file_uploader("Upload CSV", type=["csv"], key="batch_upload")

    if uploaded:
        try:
            # Ensure we are reading from the start of the file
            uploaded.seek(0)
            df = pd.read_csv(uploaded)
            df.columns = [c.lower().strip().replace(" ", "_") for c in df.columns]
            
            # Auto-combine names if needed (handle both formats)
            if "name" not in df.columns:
                if "first_name" in df.columns and "last_name" in df.columns:
                    df["name"] = df["first_name"] + " " + df["last_name"]
            
            required = {"name", "email", "company", "property_address", "city", "state"}
            missing = required - set(df.columns)
            
            if missing:
                st.error(f"CSV is missing columns: {', '.join(missing)}")
                st.info("Ensure your CSV has headers like: Name (or First/Last), Email, Company, Property Address, City, State")
            else:
                st.markdown(f"**{len(df)} leads loaded:**")
                st.dataframe(df, use_container_width=True)

                if st.button(f"🚀 Process All {len(df)} Leads", type="primary",
                             use_container_width=True, key="batch_process"):
                    results_list = []
                    bar = st.progress(0)
                    status = st.empty()

                    for i, row in df.iterrows():
                        lead = row.to_dict()
                        status.markdown(f"Processing **{lead.get('name','?')}** @ **{lead.get('company','?')}** ({i+1}/{len(df)})...")
                        res = enrich_lead(lead)
                        res["_name"] = lead.get("name", "")
                        res["_company"] = lead.get("company", "")
                        res["_city"] = lead.get("city", "")
                        res["_state"] = lead.get("state", "")
                        results_list.append(res)
                        bar.progress((i + 1) / len(df))

                    status.empty()
                    st.success(f"✅ All {len(df)} leads enriched!")

                    summary_rows = []
                    for r in results_list:
                        kd = r.get("key_data_points", {})
                        summary_rows.append({
                            "Name": r.get("_name"), "Company": r.get("_company"),
                            "City": r.get("_city"), "Tier": r.get("tier", "?"),
                            "Renter %": kd.get("renter_pct"),
                            "Vacancy %": kd.get("vacancy_rate"),
                            "Rent Growth %": kd.get("rent_growth_pct"),
                            "Time Saved (min)": r.get("estimated_time_saved_minutes"),
                        })

                    sdf = pd.DataFrame(summary_rows)
                    st.markdown("### Results Summary")
                    st.dataframe(sdf, use_container_width=True)
                    st.download_button("📥 Download Results (CSV)", data=sdf.to_csv(index=False),
                                       file_name="enriched_leads.csv", mime="text/csv",
                                       use_container_width=True)

                    st.markdown("---")
                    st.markdown("### Full Results Per Lead")
                    for r in results_list:
                        label = f"{r.get('_name', '?')} @ {r.get('_company', '?')} — Tier {r.get('tier', '?')}"
                        with st.expander(label):
                            render_result(r, lead_name=r.get("_name", ""))

        except Exception as e:
            st.error(f"Error reading CSV: {e}")

    scheduled = st.session_state.get("scheduled_results", {})
    if scheduled:
        st.divider()
        st.markdown(f"### 🕘 Scheduled Run Results ({len(scheduled)} leads)")
        for key, result in scheduled.items():
            company_name = key.split("_")[0]
            with st.expander(f"{company_name} — Tier {result.get('tier', '?')}"):
                render_result(result, lead_name=company_name)
