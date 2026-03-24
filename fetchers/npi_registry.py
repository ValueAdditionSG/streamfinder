"""
NPI Registry fetcher — looks up physician NPI, specialty, and practice location.
Uses NPPES NPI Registry API (free, no key required).
"""
import requests


BASE_URL = "https://npiregistry.cms.hhs.gov/api/"


def fetch_npi(first_name: str, last_name: str, state: str = "") -> dict:
    """
    Search the NPI registry for a physician.
    Returns dict with 'physician' info and 'error'.
    """
    try:
        params = {
            "version": "2.1",
            "enumeration_type": "NPI-1",  # Individual providers
            "first_name": first_name,
            "last_name": last_name,
            "limit": 5,
        }
        if state:
            params["state"] = state

        resp = requests.get(BASE_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        results = data.get("results", [])
        if not results:
            return {"physicians": [], "error": None}

        physicians = []
        for r in results:
            basic = r.get("basic", {})
            taxonomies = r.get("taxonomies", [])
            addresses = r.get("addresses", [])

            # Primary taxonomy (specialty)
            primary_taxonomy = next(
                (t for t in taxonomies if t.get("primary")), taxonomies[0] if taxonomies else {}
            )

            # Practice address
            practice_addr = next(
                (a for a in addresses if a.get("address_purpose") == "LOCATION"),
                addresses[0] if addresses else {},
            )

            physicians.append({
                "npi": r.get("number", ""),
                "name": f"{basic.get('first_name', '')} {basic.get('last_name', '')}".strip(),
                "credential": basic.get("credential", ""),
                "specialty": primary_taxonomy.get("desc", ""),
                "taxonomy_code": primary_taxonomy.get("code", ""),
                "organization": practice_addr.get("organization_name", ""),
                "city": practice_addr.get("city", ""),
                "state": practice_addr.get("state", ""),
                "status": basic.get("status", ""),
            })

        return {"physicians": physicians, "error": None}

    except Exception as e:
        return {"physicians": [], "error": str(e)}


def parse_name(full_name: str):
    """Simple name parser — splits into first/last."""
    # Strip titles
    name = full_name.replace("Dr.", "").replace("Dr ", "").replace("MD", "").replace("PhD", "").strip()
    parts = name.strip().split()
    if len(parts) >= 2:
        return parts[0], " ".join(parts[1:])
    return name, ""
