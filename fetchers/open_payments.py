"""
CMS Open Payments fetcher — shows industry payments (from device/pharma companies) to this physician.
Uses CMS Open Payments search API + direct profile lookup.

This is GOLD for medical device sales — it shows which competitor companies
already have financial relationships with this surgeon.
"""
import requests


BASE_URL = "https://openpaymentsdata.cms.gov"


def fetch_payments(first_name: str, last_name: str, npi: str = "") -> dict:
    """
    Search Open Payments for industry payments to this physician.
    Tries the physician profile API, falls back to generating a manual lookup URL.
    """
    result = {
        "payments": [],
        "summary": {"by_company": [], "by_type": []},
        "total_amount": 0,
        "companies": [],
        "lookup_url": None,
        "error": None,
    }

    # Build the direct lookup URL for the rep to manually check
    search_query = f"{first_name}+{last_name}".replace(" ", "+")
    result["lookup_url"] = f"{BASE_URL}/search/#?query={search_query}"

    if npi:
        result["npi_url"] = f"{BASE_URL}/physician/{npi}"

    # Try the physician search endpoint
    try:
        search_url = f"{BASE_URL}/api/1/search"
        params = {"fulltext": f"{first_name} {last_name}", "index": "physician_profile_supplement"}
        resp = requests.get(search_url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results", [])

        if results:
            # Found physician profile(s)
            profiles = []
            for r in results[:3]:
                fields = r.get("fields", {})
                profiles.append({
                    "name": fields.get("physician_first_name", "") + " " + fields.get("physician_last_name", ""),
                    "npi": fields.get("physician_npi", ""),
                    "specialty": fields.get("physician_specialty", ""),
                    "state": fields.get("physician_state", ""),
                    "total": fields.get("total_amount_of_payment_usdollars", 0),
                })
            result["profiles"] = profiles
            if profiles and profiles[0].get("npi"):
                npi_found = profiles[0]["npi"]
                result["npi_url"] = f"{BASE_URL}/physician/{npi_found}"
                result["lookup_url"] = f"{BASE_URL}/physician/{npi_found}"

        return result

    except Exception as e:
        result["error"] = str(e)
        return result


def format_for_display(payment_data: dict, first_name: str, last_name: str) -> str:
    """
    Format payment data as a text summary for the AI synthesizer.
    """
    lines = []
    lookup_url = payment_data.get("lookup_url", "")

    profiles = payment_data.get("profiles", [])
    if profiles:
        lines.append(f"Physician profile(s) found in Open Payments:")
        for p in profiles:
            lines.append(f"  - {p.get('name','')} | NPI: {p.get('npi','')} | {p.get('specialty','')} | {p.get('state','')}")
        lines.append(f"  Direct profile: {payment_data.get('npi_url', lookup_url)}")
    else:
        lines.append(f"Open Payments: Manual verification required.")
        lines.append(f"  Search URL: {lookup_url}")
        lines.append(f"  Note: CMS API has limited programmatic access; rep should check manually for competitor payment history.")

    return "\n".join(lines)
