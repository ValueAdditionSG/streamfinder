"""
ClinicalTrials.gov fetcher — finds trials where this person is an investigator.
Uses ClinicalTrials.gov API v2 (free, no key required).
"""
import requests


BASE_URL = "https://clinicaltrials.gov/api/v2/studies"


def fetch_trials(investigator_name: str, max_results: int = 10) -> dict:
    """
    Search ClinicalTrials.gov for studies involving this investigator.
    Returns dict with 'trials' list and 'error'.
    """
    try:
        params = {
            "query.term": investigator_name,
            "pageSize": max_results,
            "format": "json",
            "fields": "NCTId,BriefTitle,OverallStatus,BriefSummary,Condition,InterventionName,StartDate,CompletionDate,LeadSponsorName",
        }
        resp = requests.get(BASE_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        trials = []
        for study in data.get("studies", []):
            protocol = study.get("protocolSection", {})
            id_mod = protocol.get("identificationModule", {})
            status_mod = protocol.get("statusModule", {})
            desc_mod = protocol.get("descriptionModule", {})
            sponsor_mod = protocol.get("sponsorCollaboratorsModule", {})
            conditions_mod = protocol.get("conditionsModule", {})
            interventions_mod = protocol.get("armsInterventionsModule", {})

            # Extract interventions
            interventions = []
            for iv in interventions_mod.get("interventions", []):
                interventions.append(iv.get("name", ""))

            nct_id = id_mod.get("nctId", "")
            trials.append({
                "nct_id": nct_id,
                "title": id_mod.get("briefTitle", ""),
                "status": status_mod.get("overallStatus", ""),
                "conditions": conditions_mod.get("conditions", []),
                "interventions": interventions[:3],
                "sponsor": sponsor_mod.get("leadSponsor", {}).get("name", ""),
                "summary": (desc_mod.get("briefSummary", "") or "")[:400],
                "url": f"https://clinicaltrials.gov/study/{nct_id}",
            })

        return {"trials": trials, "total_found": data.get("totalCount", 0), "error": None}

    except Exception as e:
        return {"trials": [], "total_found": 0, "error": str(e)}
