import os
import requests
from .genre_map import resolve_movie_genres, resolve_tv_genres

TMDB_BASE = "https://api.themoviedb.org/3"
POSTER_BASE = "https://image.tmdb.org/t/p/w300"
YT_THUMB = "https://img.youtube.com/vi/{key}/hqdefault.jpg"
YT_URL = "https://www.youtube.com/watch?v={key}"


def _first_yt_trailer(videos: list[dict]) -> dict | None:
    return next(
        (v for v in videos if v.get("type") == "Trailer" and v.get("site") == "YouTube"),
        None,
    )


def _movie_trailers(api_key: str, max_results: int) -> list[dict]:
    resp = requests.get(
        f"{TMDB_BASE}/movie/upcoming",
        params={"api_key": api_key, "language": "en-US", "page": 1},
        timeout=10,
    )
    resp.raise_for_status()

    trailers = []
    for m in resp.json().get("results", [])[:20]:
        if len(trailers) >= max_results:
            break
        vids = requests.get(
            f"{TMDB_BASE}/movie/{m['id']}/videos",
            params={"api_key": api_key, "language": "en-US"},
            timeout=10,
        )
        if vids.status_code != 200:
            continue
        trailer = _first_yt_trailer(vids.json().get("results", []))
        if not trailer:
            continue
        trailers.append({
            "kind": "movie",
            "title": m["title"],
            "release_date": m.get("release_date", ""),
            "genres": resolve_movie_genres(m.get("genre_ids", [])),
            "poster": f"{POSTER_BASE}{m['poster_path']}" if m.get("poster_path") else None,
            "trailer_name": trailer.get("name", "Official Trailer"),
            "thumb": YT_THUMB.format(key=trailer["key"]),
            "url": YT_URL.format(key=trailer["key"]),
        })
    return trailers


def _tv_trailers(api_key: str, max_results: int) -> list[dict]:
    resp = requests.get(
        f"{TMDB_BASE}/tv/on_the_air",
        params={"api_key": api_key, "language": "en-US", "page": 1},
        timeout=10,
    )
    resp.raise_for_status()

    trailers = []
    for s in resp.json().get("results", [])[:20]:
        if len(trailers) >= max_results:
            break
        vids = requests.get(
            f"{TMDB_BASE}/tv/{s['id']}/videos",
            params={"api_key": api_key, "language": "en-US"},
            timeout=10,
        )
        if vids.status_code != 200:
            continue
        trailer = _first_yt_trailer(vids.json().get("results", []))
        if not trailer:
            continue
        trailers.append({
            "kind": "tv",
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
    # 3 movie trailers + 2 TV trailers = 5 total
    return _movie_trailers(api_key, 3) + _tv_trailers(api_key, 2)
