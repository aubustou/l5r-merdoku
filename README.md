# Merdoku — L5R Relic & Ritual

A deck browser for the Legend of the Five Rings Collectible Card Game. View, filter, and search your deck, and look up cards via the Oracle of the Void API (with a Claude AI fallback).

## Features

- Card gallery with filter by type, full-text search, and sort by name / cost / force / chi
- Oracle card lookup — queries [oracleofthevoid.com](https://oracleofthevoid.com); falls back to Claude AI when the API returns no results
- HTMX-driven UI — no JS framework, partial page updates via `hx-*` attributes
- "Add to Deck" from Oracle results, with automatic gallery refresh

## Setup

```bash
pip install -e .                        # requires Python 3.11+
python -m app.seed                      # load sample Scorpion Clan deck
export ANTHROPIC_API_KEY=sk-ant-...     # optional — enables Oracle AI fallback
uvicorn app.main:app --reload
```

App runs at **http://localhost:8000**. The SQLite database (`merdoku.db`) is created automatically on first startup.

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
| `static/` | CSS and JS assets |
| `Merdoku.html` | Standalone React prototype (no build step) |
