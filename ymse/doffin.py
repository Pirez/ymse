"""Search Norwegian public procurement notices on Doffin."""

import os
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv
from loguru import logger

DEFAULT_BASE_URL = "https://api.doffin.no/public/v2/"


def search_doffin(
    queries: str | list[str],
    days: int = 7,
    api_key: str | None = None,
    status: str = "",
    notice_type: str = "",
    page_size: int = 100,
    max_results: int = 100,
) -> list[dict]:
    """Search Doffin for recent notices and return a flat list of notice dicts.

    Each dict has: id, title, description, buyer, type, published, value,
    currency, url, query.

    :param queries: One search string or a list of them.
    :param days: Only include notices published within the last `days` days.
    :param api_key: Doffin subscription key; defaults to the DOFFIN_API_KEY env var.
    :param status: Optional notice status filter.
    :param notice_type: Optional notice type filter.
    :param page_size: Hits per page, used to detect the last page.
    :param max_results: Maximum notices to return per query.
    :raises KeyError: If no API key is given and DOFFIN_API_KEY is unset.
    :raises requests.HTTPError: On a non-2xx response.
    """
    load_dotenv()
    if api_key is None:
        api_key = os.environ["DOFFIN_API_KEY"]
    base_url = os.environ.get("DOFFIN_BASE_URL", DEFAULT_BASE_URL)
    if isinstance(queries, str):
        queries = [queries]
    published_after = (datetime.today() - timedelta(days=days)).strftime("%Y-%m-%d")
    headers = {"Ocp-Apim-Subscription-Key": api_key.strip()}
    results = []

    for query in queries:
        logger.info(
            "Searching Doffin: query={!r} days={} since={}",
            query,
            days,
            published_after,
        )
        page = 1
        fetched = 0
        while fetched < max_results:
            params = {
                "page": page,
                "numHitsPerPage": 100,
                "searchString": query,
                "sortBy": "PUBLICATION_DATE_DESC",
                "issueDateFrom": published_after,
            }
            if status:
                params["status"] = status
            if notice_type:
                params["type"] = notice_type

            r = requests.get(
                f"{base_url}/search", params=params, headers=headers, timeout=15
            )
            r.raise_for_status()
            data = r.json()
            hits = data.get("hits") or []
            if not hits:
                break

            remaining = max_results - fetched
            for n in hits[:remaining]:
                notice_id = n.get("id", "")
                buyers = n.get("buyer") or []
                estimated = n.get("estimatedValue") or {}
                results.append(
                    {
                        "id": notice_id,
                        "title": n.get("heading", ""),
                        "description": n.get("description", ""),
                        "buyer": buyers[0].get("name", "") if buyers else "",
                        "type": n.get("type", ""),
                        "published": (
                            n.get("issueDate") or n.get("publicationDate") or ""
                        )[:10],
                        "value": estimated.get("amount"),
                        "currency": estimated.get("currencyCode", ""),
                        "url": f"https://doffin.no/notices/{notice_id}"
                        if notice_id
                        else "",
                        "query": query,
                    }
                )

            fetched += len(hits)
            logger.debug(
                "query={!r} page={} fetched={} total_so_far={}",
                query,
                page,
                len(hits),
                fetched,
            )
            if len(hits) < page_size:
                break
            page += 1

        logger.info(
            "query={!r} done — {} notices found",
            query,
            sum(1 for r in results if r["query"] == query),
        )

    return results


if __name__ == "__main__":
    # Quick test
    notices = search_doffin("maskinlæring", days=31, max_results=100)
    for n in notices:
        print(
            f"{n['published']} | {n['title']} | {n['buyer']} | {n['type']} | {n['value']} {n['currency']} | {n['url']}"
        )
