from urllib.parse import quote
from fastapi.templating import Jinja2Templates
from app.models import CLAN_COLORS, TYPE_COLORS, LIGHTS

templates = Jinja2Templates(directory="templates")


def _card_light(title: str) -> dict:
    seed = sum(ord(c) for c in title)
    return LIGHTS[seed % len(LIGHTS)]


def _clan_style(clan: str) -> dict:
    return CLAN_COLORS.get(clan, CLAN_COLORS["default"])


templates.env.globals["clan_colors"] = CLAN_COLORS
templates.env.globals["type_colors"] = TYPE_COLORS
templates.env.filters["card_light"] = _card_light
templates.env.filters["clan_style"] = _clan_style
templates.env.filters["urlencode"] = lambda s: quote(str(s), safe="")
