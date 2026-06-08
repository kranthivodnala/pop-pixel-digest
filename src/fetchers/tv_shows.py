import os
import requests

TMDB_BASE = "https://api.themoviedb.org/3"
POSTER_BASE = "https://image.tmdb.org/t/p/w200"


def fetch_tv_shows() -> list[dict]:
    api_key = os.environ["TMDB_API_KEY"]
    resp = requests.get(
        f"{TMDB_BASE}/tv/airing_today",
        params={"api_key": api_key, "language": "en-US", "page": 1},
        timeout=10,
    )
    resp.raise_for_status()

    results = []
    for s in resp.json().get("results", [])[:6]:
        results.append({
            "name": s["name"],
            "overview": s.get("overview", ""),
            "first_air_date": s.get("first_air_date", ""),
            "rating": round(s.get("vote_average", 0), 1),
            "poster": f"{POSTER_BASE}{s['poster_path']}" if s.get("poster_path") else None,
        })
    return results
