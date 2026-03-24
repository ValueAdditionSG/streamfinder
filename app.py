"""
Surgeon Intelligence Agent — Streamlit UI
Pre-call intelligence for medical device sales professionals.
"""
import os
import streamlit as st
import concurrent.futures
import json

from fetchers.pubmed import fetch_publications
from fetchers.clinical_trials import fetch_trials
from fetchers.npi_registry import fetch_npi, parse_name
from fetchers.open_payments import fetch_payments
from fetchers.web_search import search_surgeon
from synthesizer import build_brief

# ── Config ─────────────────────────────────────────────────────────────────
DASHSCOPE_KEY = os.environ.get(
    "DASHSCOPE_API_KEY",
    "sk-40e569790dcf47c1b8f16ed633531502"  # fallback from openclaw config
)

st.set_page_config(
    page_title="Surgeon Intel Agent",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Styling ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .stApp { background-color: #0f1117; }
  .main-header { 
    font-size: 2rem; font-weight: 700; color: #00d4aa;
    border-bottom: 2px solid #00d4aa; padding-bottom: 0.5rem; margin-bottom: 1rem;
  }
  .section-header {
    font-size: 1.1rem; font-weight: 600; color: #ffffff;
    background: #1e2130; padding: 0.5rem 1rem; border-radius: 6px;
    border-left: 4px solid #00d4aa; margin: 1rem 0 0.5rem 0;
  }
  .metric-card {
    background: #1e2130; padding: 1rem; border-radius: 8px;
    border: 1px solid #2d3147; text-align: center;
  }
  .alert-high { background: #2d1b1b; border-left: 4px solid #ff4b4b; padding: 0.75rem; border-radius: 4px; margin: 0.5rem 0; }
  .alert-info { background: #1b2d2b; border-left: 4px solid #00d4aa; padding: 0.75rem; border-radius: 4px; margin: 0.5rem 0; }
  .alert-warn { background: #2d2a1b; border-left: 4px solid #ffa500; padding: 0.75rem; border-radius: 4px; margin: 0.5rem 0; }
  .tag { display: inline-block; background: #2d3147; color: #a0aec0; padding: 2px 10px; border-radius: 12px; font-size: 0.85rem; margin: 2px; }
  .checklist-item { padding: 4px 0; }
</style>
""", unsafe_allow_html=True)


# ── Header ───────────────────────────────────────────────────────────────────
st.markdown('<div class="main-header">🏥 Surgeon Intelligence Agent</div>', unsafe_allow_html=True)
st.caption("Pre-call intelligence for medical device sales professionals | Data: PubMed · ClinicalTrials.gov · CMS Open Payments · Web")

st.divider()

# ── Input Form ───────────────────────────────────────────────────────────────
with st.form("surgeon_lookup"):
    col1, col2, col3 = st.columns([2, 1.5, 1.5])
    with col1:
        surgeon_name = st.text_input(
            "Surgeon Name *",
            placeholder="e.g., Dr. Michael Danto",
            help="Include 'Dr.' for best results"
        )
    with col2:
        specialty = st.text_input(
            "Specialty",
            placeholder="e.g., Orthopedic Surgery",
        )
    with col3:
        institution = st.text_input(
            "Hospital / Institution",
            placeholder="e.g., Mayo Clinic",
        )

    device_context = st.text_area(
        "Your Device / Product Context (optional but recommended)",
        placeholder="e.g., Minimally invasive spinal fusion device targeting L4-S1. Key differentiators: 40% faster OR time, 2-year RCT published in Spine. Currently competing against Medtronic TLIF system.",
        height=90,
        help="Tell the agent what you're selling so it can tailor the brief to your product."
    )

    submitted = st.form_submit_button("🔍 Generate Pre-Call Brief", type="primary", use_container_width=True)

# ── Main Logic ───────────────────────────────────────────────────────────────
if submitted and surgeon_name.strip():
    name = surgeon_name.strip()
    first_name, last_name = parse_name(name)

    # Progress indicators
    progress = st.progress(0)
    status_text = st.empty()

    # ── Data Collection (parallel) ──────────────────────────────────────────
    status_text.markdown("⚙️ **Researching surgeon from 5 data sources...**")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        
        status_text.markdown("🔍 Searching NPI Registry, PubMed, ClinicalTrials.gov, CMS Open Payments, and Web...")
        
        f_npi = executor.submit(fetch_npi, first_name, last_name)
        f_pubmed = executor.submit(fetch_publications, name)
        f_trials = executor.submit(fetch_trials, name)
        f_payments = executor.submit(fetch_payments, first_name, last_name)
        f_web = executor.submit(search_surgeon, name, specialty, institution)

        npi_data = f_npi.result()
        progress.progress(20)
        pubmed_data = f_pubmed.result()
        progress.progress(40)
        trials_data = f_trials.result()
        progress.progress(60)
        payments_data = f_payments.result()
        progress.progress(75)
        web_data = f_web.result()
        progress.progress(85)

    # ── AI Synthesis ────────────────────────────────────────────────────────
    status_text.markdown("🧠 **AI synthesizing pre-call brief...**")
    
    result = build_brief(
        surgeon_name=name,
        specialty=specialty,
        institution=institution,
        device_context=device_context,
        npi_data=npi_data,
        pubmed_data=pubmed_data,
        trials_data=trials_data,
        payments_data=payments_data,
        web_data=web_data,
        api_key=DASHSCOPE_KEY,
    )

    progress.progress(100)
    status_text.empty()
    progress.empty()

    # ── Error Handling ───────────────────────────────────────────────────────
    if result.get("error") and not result.get("brief"):
        st.error(f"AI synthesis error: {result['error']}")
        with st.expander("Show raw data gathered"):
            st.json({
                "npi": npi_data,
                "pubmed": pubmed_data,
                "trials": trials_data,
                "web": web_data,
            })
        st.stop()

    brief = result["brief"]

    # ════════════════════════════════════════════════════════════════════════
    # RENDER THE BRIEF
    # ════════════════════════════════════════════════════════════════════════

    # ── Top Summary Bar ──────────────────────────────────────────────────────
    snap = brief.get("surgeon_snapshot", {})
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f"**{snap.get('name', name)}**")
        st.caption("Surgeon")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f"**{snap.get('specialty', specialty or 'N/A')}**")
        st.caption("Specialty")
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        pubs_count = pubmed_data.get("total_found", 0)
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f"**{pubs_count}**")
        st.caption("PubMed Publications")
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        total_paid = payments_data.get("total_amount", 0)
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f"**${total_paid:,.0f}**" if total_paid else "**$0**")
        st.caption("Industry Payments Received")
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # ── Main tabs ──────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Pre-Call Brief",
        "📚 Publications",
        "🔬 Clinical Trials",
        "💰 Industry Payments",
        "🌐 Web Intel"
    ])

    # ── TAB 1: Pre-Call Brief ──────────────────────────────────────────────
    with tab1:
        
        # Engagement Tier Banner
        rel = brief.get("relationship_strategy", {})
        tier = rel.get("engagement_tier", "")
        if "A" in tier.upper():
            st.markdown(f'<div class="alert-high">🔴 <strong>Priority {tier}</strong></div>', unsafe_allow_html=True)
        elif "B" in tier.upper():
            st.markdown(f'<div class="alert-warn">🟡 <strong>Priority {tier}</strong></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="alert-info">🟢 <strong>{tier}</strong></div>', unsafe_allow_html=True)

        col_left, col_right = st.columns([1.1, 0.9])

        with col_left:
            # Clinical Profile
            st.markdown('<div class="section-header">🩺 Clinical Profile</div>', unsafe_allow_html=True)
            clinical = brief.get("clinical_profile", {})
            st.markdown(f"**Primary Focus:** {clinical.get('primary_focus', 'N/A')}")
            
            interests = clinical.get("research_interests", [])
            if interests:
                st.markdown("**Research Interests:**")
                st.markdown(" ".join([f'<span class="tag">{i}</span>' for i in interests]), unsafe_allow_html=True)
            
            st.markdown(f"\n**Publications:** {clinical.get('publications_summary', 'N/A')}")
            kol = clinical.get("kol_indicators", "")
            if kol:
                st.markdown(f"**KOL Status:** {kol}")

            # Entry Points
            st.markdown('<div class="section-header">🎯 Best Entry Points</div>', unsafe_allow_html=True)
            intel = brief.get("intelligence_for_rep", {})
            for i, ep in enumerate(intel.get("strongest_entry_points", []), 1):
                st.markdown(f"**{i}.** {ep}")

            # Questions to Ask
            st.markdown('<div class="section-header">❓ Questions to Ask</div>', unsafe_allow_html=True)
            for q in intel.get("questions_to_ask", []):
                st.markdown(f"• {q}")

        with col_right:
            # Likely Objections
            st.markdown('<div class="section-header">⚠️ Likely Objections + Responses</div>', unsafe_allow_html=True)
            for obj in intel.get("likely_objections", []):
                with st.expander(f"🔴 \"{obj.get('objection', '')}\""):
                    st.markdown(f"**Your response:** {obj.get('suggested_response', '')}")

            # Industry Relationships
            st.markdown('<div class="section-header">🏢 Industry Relationships</div>', unsafe_allow_html=True)
            ind_rel = brief.get("industry_relationships", {})
            existing = ind_rel.get("existing_company_ties", [])
            if existing:
                for company in existing:
                    st.markdown(f"• {company}")
            else:
                st.markdown("_No significant industry ties on record_")
            
            notes = ind_rel.get("relationship_notes", "")
            if notes:
                st.markdown(f"\n**Notes:** {notes}")

            flags = ind_rel.get("conflict_flags", [])
            if flags:
                st.markdown("**⚠️ Flags:**")
                for flag in flags:
                    st.markdown(f'<div class="alert-high">⚠️ {flag}</div>', unsafe_allow_html=True)

            # Topics to Avoid
            avoid = intel.get("topics_to_avoid", [])
            if avoid:
                st.markdown('<div class="section-header">🚫 Topics to Avoid</div>', unsafe_allow_html=True)
                for t in avoid:
                    st.markdown(f"• {t}")

        # Pre-Call Checklist
        st.markdown('<div class="section-header">✅ Pre-Call Checklist</div>', unsafe_allow_html=True)
        checklist = brief.get("pre_call_checklist", [])
        cols = st.columns(2)
        for i, item in enumerate(checklist):
            with cols[i % 2]:
                st.checkbox(item, key=f"check_{i}")

        # Next Best Action + Long-term Play
        st.markdown('<div class="section-header">🚀 Strategy</div>', unsafe_allow_html=True)
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.markdown(f"**Next Best Action:**\n{rel.get('next_best_action', 'N/A')}")
        with col_s2:
            st.markdown(f"**12-Month Play:**\n{rel.get('long_term_play', 'N/A')}")
            kol_pot = rel.get("kol_potential", "")
            if kol_pot:
                st.markdown(f"**KOL Potential:** {kol_pot}")

        # Data Gaps
        gaps = brief.get("data_gaps", [])
        if gaps:
            with st.expander("🔍 Data Gaps — What We Don't Know Yet"):
                for g in gaps:
                    st.markdown(f"• {g}")

    # ── TAB 2: Publications ────────────────────────────────────────────────
    with tab2:
        papers = pubmed_data.get("papers", [])
        total = pubmed_data.get("total_found", 0)
        err = pubmed_data.get("error")
        
        if err:
            st.warning(f"PubMed error: {err}")
        elif not papers:
            st.info("No publications found on PubMed for this name. The surgeon may publish under a different name variation.")
        else:
            st.caption(f"Found {total} total publications. Showing most recent {len(papers)}.")
            for p in papers:
                with st.expander(f"📄 {p.get('title', 'No title')[:100]}"):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.markdown(f"**Journal:** {p.get('journal', 'N/A')}")
                        authors = p.get("authors", [])
                        if authors:
                            st.markdown(f"**Authors:** {', '.join(authors[:4])}")
                    with col2:
                        st.markdown(f"**Published:** {p.get('pubdate', 'N/A')}")
                        st.markdown(f"[View on PubMed]({p.get('url', '#')})")

    # ── TAB 3: Clinical Trials ─────────────────────────────────────────────
    with tab3:
        trials = trials_data.get("trials", [])
        total_t = trials_data.get("total_found", 0)
        err_t = trials_data.get("error")

        if err_t:
            st.warning(f"ClinicalTrials.gov error: {err_t}")
        elif not trials:
            st.info("No clinical trials found as investigator.")
        else:
            st.caption(f"Found {total_t} trials. Showing {len(trials)}.")
            for t in trials:
                status = t.get("status", "")
                icon = "🟢" if status == "RECRUITING" else "🔵" if status == "COMPLETED" else "🟡"
                with st.expander(f"{icon} {t.get('title', '')[:100]} [{status}]"):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        conditions = t.get("conditions", [])
                        if conditions:
                            st.markdown(f"**Conditions:** {', '.join(conditions[:3])}")
                        interventions = t.get("interventions", [])
                        if interventions:
                            st.markdown(f"**Interventions:** {', '.join(interventions[:3])}")
                        summary = t.get("summary", "")
                        if summary:
                            st.markdown(f"**Summary:** {summary[:300]}...")
                    with col2:
                        st.markdown(f"**Sponsor:** {t.get('sponsor', 'N/A')}")
                        st.markdown(f"[View on ClinicalTrials.gov]({t.get('url', '#')})")

    # ── TAB 4: Open Payments ──────────────────────────────────────────────
    with tab4:
        err_p = payments_data.get("error")
        total_paid = payments_data.get("total_amount", 0)
        companies = payments_data.get("summary", {}).get("by_company", [])
        ptypes = payments_data.get("summary", {}).get("by_type", [])

        if err_p:
            st.warning(f"CMS Open Payments API note: {err_p}")
            st.info("You can manually search at: https://openpaymentsdata.cms.gov/")
        elif not companies:
            st.success("✅ No industry payments on record — clean slate, no competitor ties to navigate.")
        else:
            st.error(f"⚠️ Total industry payments received: **${total_paid:,.2f}**")
            st.caption("Source: CMS Open Payments (public data). Includes consulting fees, speaking, royalties, research grants.")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**By Company:**")
                for company, amount in companies[:10]:
                    st.markdown(f"• {company}: **${amount:,.0f}**")
            with col2:
                st.markdown("**By Payment Type:**")
                for ptype, amount in ptypes[:8]:
                    st.markdown(f"• {ptype}: **${amount:,.0f}**")

    # ── TAB 5: Web Intel ──────────────────────────────────────────────────
    with tab5:
        web_results = web_data.get("results", [])
        if not web_results:
            st.info("No web results found. Try adjusting the institution name.")
        else:
            st.caption(f"{len(web_results)} web results gathered.")
            for r in web_results:
                with st.expander(f"🌐 {r.get('title', 'No title')[:80]}"):
                    st.markdown(f"**Snippet:** {r.get('snippet', 'N/A')}")
                    st.markdown(f"[Open link]({r.get('url', '#')})")

    # ── Export ────────────────────────────────────────────────────────────
    st.divider()
    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        brief_json = json.dumps(brief, indent=2)
        st.download_button(
            "⬇️ Download Brief (JSON)",
            data=brief_json,
            file_name=f"surgeon_brief_{name.replace(' ','_').lower()}.json",
            mime="application/json",
        )
    with col_exp2:
        # Plain text version for CRM paste
        plain = _brief_to_plaintext(brief, name)
        st.download_button(
            "⬇️ Download for CRM (Text)",
            data=plain,
            file_name=f"surgeon_brief_{name.replace(' ','_').lower()}.txt",
            mime="text/plain",
        )

elif submitted and not surgeon_name.strip():
    st.error("Please enter a surgeon name.")

# ── Footer ───────────────────────────────────────────────────────────────────
st.divider()
st.caption("🏥 Surgeon Intel Agent · Data from PubMed, ClinicalTrials.gov, CMS Open Payments, NPI Registry · AI synthesis by Qwen")


def _brief_to_plaintext(brief: dict, name: str) -> str:
    """Convert brief to plain text for CRM copy-paste."""
    lines = [
        f"SURGEON INTELLIGENCE BRIEF",
        f"Generated for: {name}",
        "=" * 50,
        "",
    ]
    snap = brief.get("surgeon_snapshot", {})
    lines += [
        f"Name: {snap.get('name', name)}",
        f"Specialty: {snap.get('specialty', '')}",
        f"Institution: {snap.get('institution', '')}",
        f"NPI: {snap.get('npi', 'N/A')}",
        "",
    ]

    rel = brief.get("relationship_strategy", {})
    lines += [
        f"ENGAGEMENT TIER: {rel.get('engagement_tier', '')}",
        f"NEXT BEST ACTION: {rel.get('next_best_action', '')}",
        "",
    ]

    intel = brief.get("intelligence_for_rep", {})
    lines += ["ENTRY POINTS:"]
    for ep in intel.get("strongest_entry_points", []):
        lines.append(f"  - {ep}")
    lines.append("")

    lines += ["LIKELY OBJECTIONS:"]
    for obj in intel.get("likely_objections", []):
        lines.append(f"  Q: {obj.get('objection', '')}")
        lines.append(f"  A: {obj.get('suggested_response', '')}")
    lines.append("")

    lines += ["PRE-CALL CHECKLIST:"]
    for item in brief.get("pre_call_checklist", []):
        lines.append(f"  [ ] {item}")

    return "\n".join(lines)
