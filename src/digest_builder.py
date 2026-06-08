import os
from datetime import date

from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")


def build_digest(movies: list, tv_shows: list, games: list, ott: list) -> str:
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=True)
    template = env.get_template("digest.html")
    return template.render(
        date=date.today().strftime("%B %d, %Y"),
        movies=movies,
        tv_shows=tv_shows,
        games=games,
        ott=ott,
    )
