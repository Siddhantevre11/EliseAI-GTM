# EliseAI Lead Enrichment Agent — Project Rollout Plan

## What We Built

An agentic AI pipeline that takes a raw inbound lead (name, email, company, address) and outputs:
- **Tier A/B/C score** with plain-English rationale citing real data
- **Personalized draft email** referencing specific market signals
- **3 SDR talking points** backed by enriched data
- **Estimated time saved** per lead vs. manual research

**Core design**: Claude `tool_use` as the reasoning engine calling Census, WalkScore, FRED, and NewsAPI — not a formula, but actual reasoning about EliseAI's ICP.

---

## Phase 1: MVP Testing (Weeks 1–2)

**Objective**: Validate that the tool saves real time and improves output quality.

### Who's involved
- 2 SDRs (ideally your highest-volume reps — most data, most feedback)
- SDR Manager (owns the process, tracks outcomes)
- 1 RevOps / Sales Ops person (CRM access, data hygiene)

### What they do
- Run the tool on 10 real inbound leads they've already worked manually
- Compare: tool-generated tier vs. their own intuition. Does it agree?
- Compare: tool-generated email vs. what they sent. Is the tool's version better?
- Rate the talking points (1–5): would you actually use these on a call?
- Track actual time: how long does the full enrichment take vs. what it was before?

### Success criteria
| Metric | Target |
|---|---|
| Time to enrich 1 lead | < 90 seconds |
| SDR agreement with tier | > 70% |
| SDR rates email ≥ 4/5 | > 60% of leads |
| Zero broken runs on valid US addresses | 100% |

### Assumption to validate
The single biggest assumption in the scoring model is that renter % and market density are the strongest proxy for EliseAI's addressable market. Two weeks with real SDRs either confirms this or surfaces better signals.

---

## Phase 2: Process Integration (Weeks 3–4)

**Objective**: Embed the tool in the actual SDR workflow, not just as a side experiment.

### Changes to the workflow
1. **New lead arrives** (CRM / spreadsheet / HubSpot form) → drops into `sample_leads.csv` or hits a webhook
2. **Tool auto-runs** (daily 9am scheduler OR on-demand button)
3. **Enriched brief lands in the SDR's queue** before they start their day
4. **SDR uses the brief, not raw lead data**, as their research starting point

### What SDRs should NOT do anymore
- Google the company manually
- Look up Census data by hand
- Write generic cold emails from scratch

### What SDRs still own
- Qualifying the lead further on the call
- Deciding whether to send the email as-is or personalize further
- Managing the relationship

### Integration options (pick one for now)
- **Option A: CSV workflow** — RevOps adds new leads to a shared `leads_input.csv` each morning; tool processes at 9am; SDRs open Streamlit to see results
- **Option B: Manual trigger** — SDR pastes lead into Streamlit form, clicks "Enrich", gets results in 90 seconds
- **Option C (later): CRM webhook** — HubSpot/Salesforce sends new lead to a FastAPI endpoint, result written back as a note

Start with A or B. Option C is a Phase 3 upgrade.

---

## Phase 3: Full Team Rollout (Weeks 5–6)

**Objective**: Roll out to all SDRs with documented process and SLAs.

### Rollout steps
1. Run a 30-minute group demo session ("here's what it does, here's what it doesn't do")
2. Create a 1-page SOP: when to use it, what to trust, how to flag bad outputs
3. Assign RevOps to monitor API usage / costs / errors weekly
4. Set a 30-day retrospective to review: did Tier A leads actually convert at higher rates?

### Stakeholders

| Stakeholder | Role | Why they matter |
|---|---|---|
| SDR Manager | Champion & process owner | Owns SDR workflow, sets expectations |
| RevOps / Sales Ops | Data + CRM integration | Handles lead routing, CSV hygiene, reporting |
| IT / Security | API key management | Needs to know keys are in `.env`, not hardcoded |
| Sales Leadership | Business case + metrics | Will ask: "Did this move the needle on pipeline?" |
| SDRs (users) | Day-to-day usage | Their buy-in is required for adoption |

---

## Key Metrics to Track Post-Rollout

| Metric | How to measure | Target |
|---|---|---|
| Time-to-first-outreach | CRM timestamps: lead created → first email sent | < 2 hours for Tier A |
| Reply rate on AI-drafted emails | Email open + reply rate via HubSpot/Salesloft | +15% vs. baseline |
| SDR time on research | Self-reported in weekly standup | -30 min/day |
| Tier accuracy | Track which tiers actually converted | Tier A converts 3× more than C |
| Tool uptime / error rate | Log errors in `app.py` | < 5% failed runs |

---

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| API rate limits (NewsAPI: 100/day free tier) | Cache results in session state; upgrade to paid plan ($449/mo) when needed |
| Rural / non-US addresses return no data | All wrappers have `None` fallbacks; Claude's prompt handles missing data gracefully |
| Claude hallucinates company details | Prompt explicitly requires citing only data from tool results; SDR reviews before sending |
| SDRs don't trust it and skip it | SOPs + weekly review of cases where tool agreed / disagreed with rep intuition |
| API keys in wrong hands | Keys in `.env`, never committed to Git; IT manages via password manager |

---

## Timeline Summary

| Week | Milestone |
|---|---|
| 1 | Setup + pilot with 2 SDRs on 10 backdated leads |
| 2 | Collect feedback, tune system prompt if needed |
| 3 | Integrate into daily workflow (CSV or manual trigger) |
| 4 | Expand to 5 SDRs, monitor errors, gather usage data |
| 5 | Full team rollout + SOP documentation |
| 6 | 30-day retrospective: is Tier A converting? |
| Month 2+ | CRM webhook integration, automated follow-up suggestions |

---

## Assumptions Made in Scoring Logic

| Assumption | Rationale |
|---|---|
| Renter % > 55% is a strong positive signal | More renters = larger addressable base for leasing automation |
| Company managing 500+ units is the unit threshold | Below this, ROI on EliseAI is harder to justify |
| Urban / high Walk Score correlates with multifamily density | Walkable cities skew toward rental apartments, not suburban SFR |
| PE-backed or institutionally owned = budget + scaling pressure | These operators are under margin pressure and value tech ROI |
| Rent growth > 3% YoY = operator pressure to optimize | Rising rents + high inquiry volume → need to centralize and automate |
| Recent news of expansion = near-term buying signal | Operators adding units need leasing infra to scale |

These assumptions are based on publicly available EliseAI customer profiles and standard multifamily industry dynamics. They should be validated against actual CRM conversion data over time.
