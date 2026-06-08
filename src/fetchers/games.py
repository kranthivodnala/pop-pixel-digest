import os
import requests
from datetime import date, timedelta

RAWG_BASE = "https://api.rawg.io/api"


def fetch_games() -> list[dict]:
    api_key = os.environ["RAWG_API_KEY"]
    today = date.today().isoformat()
    week_ago = (date.today() - timedelta(days=7)).isoformat()

    resp = requests.get(
        f"{RAWG_BASE}/games",
        params={
            "key": api_key,
            "dates": f"{week_ago},{today}",
            "ordering": "-rating",
            "page_size": 6,
        },
        timeout=10,
    )
    resp.raise_for_status()

    results = []
    for g in resp.json().get("results", []):
        results.append({
            "name": g["name"],
            "released": g.get("released", ""),
            "rating": round(g.get("rating", 0), 1),
            "platforms": [p["platform"]["name"] for p in g.get("platforms", [])[:4]],
            "poster": g.get("background_image"),
        })
    return results
