# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the App

```bash
# Install dependencies (requires Python 3.14+)
pip install -e .

# Seed the database with the sample Scorpion Clan deck
python -m app.seed

# Start the dev server
uvicorn app.main:app --reload
```

The app runs at `http://localhost:8000`. The SQLite database (`merdoku.db`) is created automatically on first startup via `Base.metadata.create_all`.

The `ANTHROPIC_API_KEY` environment variable is optional; the Oracle AI fallback is disabled when it is not set.

## Running with Docker

```bash
export ANTHROPIC_API_KEY=sk-ant-...     # optional
docker compose up --build
```

The SQLite database is stored in a named volume (`db-data`). Override the path via `DATABASE_URL` (e.g. `sqlite:///data/merdoku.db`). The `app/database.py` module reads this variable at startup.

## Running Tests

```bash
pip install -e ".[test]"
playwright install chromium
pytest
```

Tests use `pytest-playwright` against a real uvicorn server (port 8791) backed by an isolated SQLite test DB (`test_merdoku.db`, deleted after the session). The `get_db` dependency is overridden so the app DB is never touched. Oracle API calls are mocked — no `ANTHROPIC_API_KEY` needed.

HTMX is served from `static/js/htmx.min.js` (bundled locally) so tests work without internet access.

## Architecture

**Stack:** FastAPI + SQLAlchemy (SQLite) + Jinja2 templates + HTMX for partial updates. No JS framework — interactivity is driven by HTMX attributes on HTML elements.

**Request flow:**
- `GET /` — full page render via `cards.router`, returns `index.html` extending `base.html`
- `GET /cards/grid` — HTMX partial, returns `partials/card_grid.html` (re-renders card tiles on filter/search/sort)
- `GET /cards/{title}/detail` — HTMX partial for modal card detail view
- `POST /cards/add` — adds a card, fires `HX-Trigger: cardsChanged` which causes the grid to auto-refresh
- `POST /oracle/lookup` — looks up a card by name, returns `partials/oracle_result.html`; the result has an "Add to Deck" button that posts to `/cards/add`

**Oracle lookup** (`app/routers/oracle.py`): tries `https://api.oracleofthevoid.com/search` first; falls back to Claude (`claude-opus-4-5`) if the API returns no results. The Claude prompt instructs the model to call the Oracle API as a tool and return structured JSON.

**Templates** (`app/templates.py`): Jinja2 env is extended with `clan_style` and `card_light` filters, plus `clan_colors`/`type_colors` globals. `card_light` deterministically picks a CSS filter+object-position combo from `LIGHTS` based on the card title hash.

**Models** (`app/models.py`): Single `Card` table. `CLAN_COLORS`, `TYPE_COLORS`, `CARD_TYPE_ORDER`, and `LIGHTS` are defined here and imported by both the router and templates module.

**Static prototype:** `Merdoku.html` is a standalone single-file React prototype (no build step, uses Babel standalone). The `tweaks-panel.jsx` is the source for the tweaks/settings panel used in the static prototype.

**HTMX:** bundled locally at `static/js/htmx.min.js` (v2.0.4) and loaded from there in `base.html`. Do not switch back to the CDN — tests run offline.
