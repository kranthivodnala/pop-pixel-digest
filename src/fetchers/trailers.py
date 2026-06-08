import os
import requests
from .genre_map import resolve_movie_genres, resolve_tv_genres

TMDB_BASE = "https://api.themoviedb.org/3"
POSTER_BASE = "https://image.tmdb.org/t/p/w300"
YT_THUMB = "https://img.youtube.com/vi/{key}/hqdefault.jpg"
YT_URL = "https://www.youtube.com/watch?v={key}"

# (region, display_label) — IN covers Bollywood, Tamil, Telugu, Malayalam, Kannada
REGIONS = [
    ("US", "en-US", "International"),
    ("IN", "hi-IN", "Indian"),
]


def _first_yt_trailer(videos: list[dict]) -> dict | None:
    return next(
        (v for v in videos if v.get("type") == "Trailer" and v.get("site") == "YouTube"),
        None,
    )


def _fetch_videos(api_key: str, media_type: str, media_id: int) -> list[dict]:
    # Fetch without a language filter so we get native-language trailers too
    resp = requests.get(
        f"{TMDB_BASE}/{media_type}/{media_id}/videos",
        params={"api_key": api_key},
        timeout=10,
    )
    return resp.json().get("results", []) if resp.status_code == 200 else []


def _movie_trailers(api_key: str, region: str, language: str, label: str, max_results: int) -> list[dict]:
    resp = requests.get(
        f"{TMDB_BASE}/movie/upcoming",
        params={"api_key": api_key, "language": language, "region": region, "page": 1},
        timeout=10,
    )
    resp.raise_for_status()

    trailers = []
    for m in resp.json().get("results", [])[:20]:
        if len(trailers) >= max_results:
            break
        trailer = _first_yt_trailer(_fetch_videos(api_key, "movie", m["id"]))
        if not trailer:
            continue
        trailers.append({
            "kind": "movie",
            "region_label": label,
            "title": m["title"],
            "release_date": m.get("release_date", ""),
            "genres": resolve_movie_genres(m.get("genre_ids", [])),
            "poster": f"{POSTER_BASE}{m['poster_path']}" if m.get("poster_path") else None,
            "trailer_name": trailer.get("name", "Official Trailer"),
            "thumb": YT_THUMB.format(key=trailer["key"]),
            "url": YT_URL.format(key=trailer["key"]),
        })
    return trailers


def _tv_trailers(api_key: str, region: str, language: str, label: str, max_results: int) -> list[dict]:
    resp = requests.get(
        f"{TMDB_BASE}/tv/on_the_air",
        params={"api_key": api_key, "language": language, "region": region, "page": 1},
        timeout=10,
    )
    resp.raise_for_status()

    trailers = []
    for s in resp.json().get("results", [])[:20]:
        if len(trailers) >= max_results:
            break
        trailer = _first_yt_trailer(_fetch_videos(api_key, "tv", s["id"]))
        if not trailer:
            continue
        trailers.append({
            "kind": "tv",
            "region_label": label,
            "title": s["name"],
            "release_date": s.get("first_air_date", ""),
            "genres": resolve_tv_genres(s.get("genre_ids", [])),
            "poster": f"{POSTER_BASE}{s['poster_path']}" if s.get("poster_path") else None,
            "trailer_name": trailer.get("name", "Official Trailer"),
            "thumb": YT_THUMB.format(key=trailer["key"]),
            "url": YT_URL.format(key=trailer["key"]),
        })
    return trailers


def fetch_trailers() -> list[dict]:
    api_key = os.environ["TMDB_API_KEY"]

    seen: set[str] = set()
    results: list[dict] = []

    for region, language, label in REGIONS:
        # 1 movie + 1 TV per region = 2 per region × 2 regions = 4 total
        for t in _movie_trailers(api_key, region, language, label, 1) + \
                 _tv_trailers(api_key, region, language, label, 1):
            key = t["title"].lower()
            if key not in seen:
                seen.add(key)
                results.append(t)

    return results
