import os
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv
from loguru import logger

BASE_URL = "https://api.doffin.no/public/v2"


def search_doffin(
    queries: str | list[str],
    days: int = 7,
    api_key: str | None = None,
    status: str = "",
    notice_type: str = "",
    page_size: int = 100,
    max_results: int = 500,
) -> list[dict]:
    """
    Search Doffin for notices published within the last `days` days.
    Accepts one or multiple queries; returns a combined flat list of notice dicts.
    Each dict contains: id, title, description, buyer, type, published,
    value, currency, url, query.
    API key is read from DOFFIN_API_KEY env var if not provided.
    """
    load_dotenv()
    if api_key is None:
        api_key = os.environ["DOFFIN_API_KEY"]
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
                "numHitsPerPage": page_size,
                "searchString": query,
                "issueDateFrom": published_after,
            }
            if status:
                params["status"] = status
            if notice_type:
                params["type"] = notice_type

            r = requests.get(
                f"{BASE_URL}/search", params=params, headers=headers, timeout=15
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
