import sys
from dotenv import load_dotenv

load_dotenv()

from src.fetchers.movies import fetch_movies
from src.fetchers.tv_shows import fetch_tv_shows
from src.fetchers.games import fetch_games
from src.fetchers.ott import fetch_ott_releases
from src.digest_builder import build_digest
from src.email_sender import send_digest
from src.subscriber_manager import get_all_subscribers


def _safe_fetch(name: str, fn):
    try:
        return fn()
    except Exception as exc:
        print(f"[WARN] {name} fetch failed: {exc}")
        return []


def main() -> None:
    print("Fetching content...")
    movies   = _safe_fetch("movies",   fetch_movies)
    tv_shows = _safe_fetch("tv_shows", fetch_tv_shows)
    games    = _safe_fetch("games",    fetch_games)
    ott      = _safe_fetch("ott",      fetch_ott_releases)

    print(f"  movies={len(movies)}, tv={len(tv_shows)}, games={len(games)}, ott={len(ott)}")

    html = build_digest(movies=movies, tv_shows=tv_shows, games=games, ott=ott)

    subscribers = get_all_subscribers()
    if not subscribers:
        print("No active subscribers. Exiting.")
        sys.exit(0)

    print(f"Sending to {len(subscribers)} subscriber(s)...")
    ok = sum(send_digest(email, html) for email in subscribers)
    print(f"Done. {ok}/{len(subscribers)} emails sent.")


if __name__ == "__main__":
    main()
