import os
import requests
from datetime import date, timedelta
from .genre_map import resolve_movie_genres

TMDB_BASE = "https://api.themoviedb.org/3"
POSTER_BASE = "https://image.tmdb.org/t/p/w300"

# (provider_id, display_name, region)
PROVIDERS = [
    (8,   "Netflix",             "US"),
    (9,   "Amazon Prime Video",  "US"),
    (337, "Disney+",             "US"),
    (350, "Apple TV+",           "US"),
    (387, "Max",                 "US"),
    (15,  "Hulu",                "US"),
    (122, "Disney+ Hotstar",     "IN"),
    (237, "SonyLIV",             "IN"),
    (220, "Zee5",                "IN"),
]


def fetch_ott_releases() -> list[dict]:
    api_key = os.environ["TMDB_API_KEY"]
    today = date.today().isoformat()
    week_ago = (date.today() - timedelta(days=7)).isoformat()

    seen: set[int] = set()
    results: list[dict] = []

    for provider_id, provider_name, region in PROVIDERS:
        resp = requests.get(
            f"{TMDB_BASE}/discover/movie",
            params={
                "api_key": api_key,
                "language": "en-US",
                "with_watch_providers": str(provider_id),
                "watch_region": region,
                "sort_by": "primary_release_date.desc",
                "primary_release_date.gte": week_ago,
                "primary_release_date.lte": today,
                "page": 1,
            },
            timeout=10,
        )
        if resp.status_code != 200:
            continue

        for m in resp.json().get("results", [])[:2]:
            if m["id"] in seen:
                continue
            seen.add(m["id"])
            results.append({
                "title": m["title"],
                "overview": m.get("overview", ""),
                "release_date": m.get("release_date", ""),
                "rating": round(m.get("vote_average", 0), 1),
                "genres": resolve_movie_genres(m.get("genre_ids", [])),
                "poster": f"{POSTER_BASE}{m['poster_path']}" if m.get("poster_path") else None,
                "provider": provider_name,
            })

        if len(results) >= 8:
            break

    return results
