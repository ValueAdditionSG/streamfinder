"""
Synthesizer — takes all raw data gathered by the fetchers and uses an LLM
to produce a structured, actionable Pre-Call Brief for a medical device sales rep.
"""
import json
from openai import OpenAI


# DashScope (Qwen) — OpenAI-compatible endpoint
DASHSCOPE_BASE = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
MODEL = "qwen-plus"  # Good balance of speed + quality; upgrade to qwen-max if needed


def build_brief(
    surgeon_name: str,
    specialty: str,
    institution: str,
    device_context: str,
    npi_data: dict,
    pubmed_data: dict,
    trials_data: dict,
    payments_data: dict,
    web_data: dict,
    api_key: str,
) -> dict:
    """
    Synthesize all data sources into an actionable pre-call brief.
    Returns dict with sections of the brief.
    """
    client = OpenAI(api_key=api_key, base_url=DASHSCOPE_BASE)

    # --- Build the data summary for the prompt ---
    data_summary = _build_data_summary(
        surgeon_name, specialty, institution,
        npi_data, pubmed_data, trials_data, payments_data, web_data
    )

    system_prompt = """You are an expert medical device sales intelligence analyst. 
Your job is to take raw research data about a surgeon and produce a sharp, actionable 
pre-call brief for a medical device sales representative.

Be concise, specific, and practical. Focus on what the rep can USE in the conversation.
Avoid generic statements. Every insight should be tied to the actual data provided.
Output valid JSON only — no markdown, no commentary outside the JSON."""

    user_prompt = f"""Here is the raw research data for a surgeon that a medical device rep is about to call on:

DEVICE/PRODUCT CONTEXT:
{device_context if device_context else "Medical device (general - no specific product specified)"}

RAW DATA:
{data_summary}

Generate a structured Pre-Call Brief as JSON with EXACTLY this structure:
{{
  "surgeon_snapshot": {{
    "name": "Full name with credentials",
    "specialty": "Primary specialty and sub-specialty if known",
    "institution": "Current institution/hospital",
    "npi": "NPI number if found",
    "profile_confidence": "high/medium/low (based on data quality)"
  }},
  "clinical_profile": {{
    "primary_focus": "Their main clinical focus areas (from publications/trials)",
    "research_interests": ["list", "of", "key", "research", "themes"],
    "procedure_types": ["likely", "procedure", "types", "they", "perform"],
    "publications_summary": "1-2 sentence summary of their publishing activity",
    "kol_indicators": "Are they a Key Opinion Leader? Evidence from data."
  }},
  "industry_relationships": {{
    "existing_company_ties": ["list of companies they have financial relationships with"],
    "total_payments_received": "Total $ amount if available",
    "relationship_notes": "Notable relationships — e.g., competitor consulting, royalties",
    "conflict_flags": ["Any flags that could complicate your pitch"]
  }},
  "intelligence_for_rep": {{
    "strongest_entry_points": ["Top 2-3 angles most likely to resonate with THIS surgeon"],
    "likely_objections": [
      {{"objection": "What they might say", "suggested_response": "How to address it with evidence"}}
    ],
    "questions_to_ask": ["Smart discovery questions based on their profile"],
    "topics_to_avoid": ["Things that could backfire based on their background"],
    "recommended_evidence": ["Specific study types or data points most relevant to them"]
  }},
  "relationship_strategy": {{
    "engagement_tier": "Priority A/B/C and why",
    "kol_potential": "Could this person become an advocate? Evidence.",
    "next_best_action": "Specific recommended first move for the rep",
    "long_term_play": "How to develop this relationship over 6-12 months"
  }},
  "pre_call_checklist": [
    "Action item 1 to prepare for the call",
    "Action item 2",
    "Action item 3"
  ],
  "data_gaps": ["What we don't know that would be valuable to find out"]
}}"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=2500,
        )

        raw_output = response.choices[0].message.content.strip()

        # Strip markdown code fences if present
        if raw_output.startswith("```"):
            raw_output = raw_output.split("```")[1]
            if raw_output.startswith("json"):
                raw_output = raw_output[4:]
        raw_output = raw_output.strip()

        brief = json.loads(raw_output)
        return {"brief": brief, "error": None}

    except json.JSONDecodeError as e:
        return {"brief": None, "raw_output": raw_output, "error": f"JSON parse error: {e}"}
    except Exception as e:
        return {"brief": None, "error": str(e)}


def _build_data_summary(
    surgeon_name, specialty, institution,
    npi_data, pubmed_data, trials_data, payments_data, web_data
) -> str:
    """Format all raw data into a clean text block for the LLM prompt."""
    parts = []

    parts.append(f"SURGEON: {surgeon_name}")
    if specialty:
        parts.append(f"SPECIALTY: {specialty}")
    if institution:
        parts.append(f"INSTITUTION: {institution}")

    # NPI data
    physicians = npi_data.get("physicians", [])
    if physicians:
        p = physicians[0]
        parts.append(f"\nNPI REGISTRY MATCH:")
        parts.append(f"  NPI: {p.get('npi')}")
        parts.append(f"  Specialty: {p.get('specialty')}")
        parts.append(f"  Location: {p.get('city')}, {p.get('state')}")
        parts.append(f"  Organization: {p.get('organization')}")
    else:
        parts.append("\nNPI REGISTRY: No match found")

    # PubMed
    papers = pubmed_data.get("papers", [])
    total_pubs = pubmed_data.get("total_found", 0)
    if papers:
        parts.append(f"\nPUBMED PUBLICATIONS ({total_pubs} total found, showing {len(papers)}):")
        for p in papers[:10]:
            parts.append(f"  [{p.get('pubdate', '')}] {p.get('title', '')}")
            parts.append(f"    Journal: {p.get('journal', '')}")
    else:
        parts.append("\nPUBMED: No publications found (may indicate early-career or name variation)")

    # Clinical Trials
    trials = trials_data.get("trials", [])
    if trials:
        parts.append(f"\nCLINICAL TRIALS ({trials_data.get('total_found', 0)} found):")
        for t in trials[:5]:
            parts.append(f"  [{t.get('status')}] {t.get('title', '')}")
            parts.append(f"    Sponsor: {t.get('sponsor', 'N/A')}")
            if t.get("conditions"):
                parts.append(f"    Conditions: {', '.join(t['conditions'][:3])}")
    else:
        parts.append("\nCLINICAL TRIALS: No trials found as investigator")

    # Open Payments
    from fetchers.open_payments import format_for_display
    parts.append(f"\nCMS OPEN PAYMENTS:")
    parts.append(format_for_display(payments_data, "", ""))

    # Web search
    web_results = web_data.get("results", [])
    if web_results:
        parts.append(f"\nWEB INTELLIGENCE ({len(web_results)} results):")
        for r in web_results[:6]:
            parts.append(f"  [{r.get('title', '')}]")
            parts.append(f"    {r.get('snippet', '')[:200]}")
            parts.append(f"    URL: {r.get('url', '')}")

    return "\n".join(parts)
