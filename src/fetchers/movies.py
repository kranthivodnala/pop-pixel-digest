import os
import requests
from .genre_map import resolve_movie_genres

TMDB_BASE = "https://api.themoviedb.org/3"
POSTER_BASE = "https://image.tmdb.org/t/p/w300"


def fetch_movies() -> list[dict]:
    api_key = os.environ["TMDB_API_KEY"]
    resp = requests.get(
        f"{TMDB_BASE}/movie/now_playing",
        params={"api_key": api_key, "language": "en-US", "page": 1},
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
            "genres": resolve_movie_genres(m.get("genre_ids", [])),
            "poster": f"{POSTER_BASE}{m['poster_path']}" if m.get("poster_path") else None,
        })
    return results
