"""
Web search fetcher — uses local SearXNG instance to gather general
web intelligence: hospital bio, news, conference talks, interviews.
"""
import requests
import json


SEARXNG_URL = "http://localhost:8080"


def search_surgeon(name: str, specialty: str = "", institution: str = "", max_results: int = 8) -> dict:
    """
    Search the web for public information about this surgeon.
    Returns dict with 'results' list and 'error'.
    """
    queries = []

    # Build targeted queries
    base = name
    if institution:
        base += f" {institution}"

    queries.append(f'"{name}" surgeon {specialty} {institution}'.strip())
    queries.append(f'"{name}" medical device OR implant OR surgery')
    queries.append(f'"{name}" conference OR keynote OR speaker OR presentation')

    all_results = []
    seen_urls = set()

    for query in queries[:2]:  # Run top 2 queries to stay fast
        try:
            resp = requests.get(
                f"{SEARXNG_URL}/search",
                params={
                    "q": query,
                    "format": "json",
                    "categories": "general",
                    "language": "en",
                },
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()

            for r in data.get("results", [])[:max_results]:
                url = r.get("url", "")
                if url not in seen_urls:
                    seen_urls.add(url)
                    all_results.append({
                        "title": r.get("title", ""),
                        "url": url,
                        "snippet": r.get("content", "")[:300],
                        "source": r.get("engine", ""),
                    })

        except Exception:
            continue

    # Deduplicate and limit
    return {"results": all_results[:12], "error": None}


def fetch_hospital_bio(name: str, institution: str) -> dict:
    """
    Try to find the surgeon's official hospital/university bio page.
    """
    try:
        query = f'"{name}" site:{institution.lower().replace(" ", "")}.org OR site:{institution.lower().replace(" ", "")}.edu biography profile'
        resp = requests.get(
            f"{SEARXNG_URL}/search",
            params={"q": query, "format": "json", "categories": "general"},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results", [])
        if results:
            return {"found": True, "url": results[0].get("url", ""), "snippet": results[0].get("content", "")[:400]}
        return {"found": False, "url": "", "snippet": ""}
    except Exception as e:
        return {"found": False, "url": "", "snippet": "", "error": str(e)}
