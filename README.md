# Merdoku — L5R Relic & Ritual

A deck browser for the Legend of the Five Rings Collectible Card Game. Browse, filter, search, and look up cards via the Oracle of the Void API (with a Claude AI fallback).

## Requirements

- Python 3.11+
- `ANTHROPIC_API_KEY` environment variable (optional — enables Oracle AI fallback)

## Setup

```bash
pip install -e .                        # requires Python 3.11+
python -m app.seed                      # load sample Scorpion Clan deck
export ANTHROPIC_API_KEY=sk-ant-...     # optional — enables Oracle AI fallback
uvicorn app.main:app --reload
```

App runs at **http://localhost:8000**. The SQLite database (`merdoku.db`) is created automatically on first startup.

## Features

- **Card gallery** — browse cards grouped by type with clan-coloured borders and art
- **Filters** — filter by card type (Personality, Holding, Strategy, Spell, Item, Stronghold…)
- **Search** — live search by card title or ability text
- **Sort** — by name, cost, force, or chi
- **Card detail modal** — full card view with Text / Keywords / Lore tabs
- **Oracle Lookup** — look up any L5R card by name; tries the [Oracle of the Void](https://oracleofthevoid.com) API first, falls back to Claude AI
- **Add to Gallery** — add Oracle results directly to your deck

## Tech stack

| Layer | Tech |
|---|---|
| Backend | FastAPI + SQLAlchemy (SQLite) |
| Templates | Jinja2 + HTMX |
| AI fallback | Anthropic Claude (`claude-opus-4-5`) |

## Project layout

| Path | Description |
|---|---|
| `app/` | FastAPI app — models, routers, templates config, seed script |
| `templates/` | Jinja2 HTML templates and HTMX partials |
| `static/` | CSS and JS assets (HTMX bundled locally) |
| `tests/` | Playwright end-to-end test suite |
| `Merdoku.html` | Standalone React prototype (no build step) |

## Running Tests

```bash
pip install -e ".[test]"
playwright install chromium
pytest
```

Tests spin up a real uvicorn server against an isolated SQLite test DB. No `ANTHROPIC_API_KEY` required — Oracle API calls are mocked.
