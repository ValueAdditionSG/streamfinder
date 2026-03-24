"""
PubMed fetcher — pulls recent publications for a given author.
Uses NCBI E-utilities (free, no API key required).
"""
import requests
import time

BASE_SEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
BASE_SUMMARY = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"


def fetch_publications(author_name: str, max_results: int = 15) -> dict:
    """
    Search PubMed for publications by this author.
    Returns a dict with 'papers' list and 'error' if something went wrong.
    """
    try:
        # Step 1: Search for PMIDs
        search_params = {
            "db": "pubmed",
            "term": f"{author_name}[Author]",
            "retmax": max_results,
            "retmode": "json",
            "sort": "date",
        }
        resp = requests.get(BASE_SEARCH, params=search_params, timeout=15)
        resp.raise_for_status()
        search_data = resp.json()
        ids = search_data.get("esearchresult", {}).get("idlist", [])

        if not ids:
            return {"papers": [], "total_found": 0, "error": None}

        total = int(search_data.get("esearchresult", {}).get("count", 0))

        # Step 2: Fetch summaries
        time.sleep(0.4)  # Be polite to NCBI
        summary_params = {
            "db": "pubmed",
            "id": ",".join(ids),
            "retmode": "json",
        }
        s_resp = requests.get(BASE_SUMMARY, params=summary_params, timeout=15)
        s_resp.raise_for_status()
        summary_data = s_resp.json()

        papers = []
        for pmid in ids:
            article = summary_data.get("result", {}).get(pmid, {})
            if not article or pmid == "uids":
                continue

            # Extract author list to confirm this is the right person
            authors = article.get("authors", [])
            author_names = [a.get("name", "") for a in authors]

            papers.append({
                "pmid": pmid,
                "title": article.get("title", "No title"),
                "journal": article.get("source", ""),
                "pubdate": article.get("pubdate", ""),
                "authors": author_names[:5],  # First 5 authors
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            })

        return {"papers": papers, "total_found": total, "error": None}

    except Exception as e:
        return {"papers": [], "total_found": 0, "error": str(e)}
