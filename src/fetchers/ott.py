import os
import requests
from datetime import date, timedelta

TMDB_BASE = "https://api.themoviedb.org/3"
POSTER_BASE = "https://image.tmdb.org/t/p/w200"

# TMDB watch provider IDs for major OTT platforms
OTT_PROVIDER_IDS = "8|9|337|350|387|15"  # Netflix|Prime|Disney+|Apple TV+|HBO Max|Hulu


def fetch_ott_releases() -> list[dict]:
    api_key = os.environ["TMDB_API_KEY"]
    today = date.today().isoformat()
    week_ago = (date.today() - timedelta(days=7)).isoformat()

    resp = requests.get(
        f"{TMDB_BASE}/discover/movie",
        params={
            "api_key": api_key,
            "language": "en-US",
            "with_watch_providers": OTT_PROVIDER_IDS,
            "watch_region": "US",
            "sort_by": "primary_release_date.desc",
            "primary_release_date.gte": week_ago,
            "primary_release_date.lte": today,
            "page": 1,
        },
        timeout=10,
    )
    resp.raise_for_status()

    results = []
    for m in resp.json().get("results", [])[:6]:
        results.append({
            "title": m["title"],
            "overview": m.get("overview", ""),
            "release_date": m.get("release_date", ""),
            "rating": round(m.get("vote_average", 0), 1),
            "poster": f"{POSTER_BASE}{m['poster_path']}" if m.get("poster_path") else None,
        })
    return results
