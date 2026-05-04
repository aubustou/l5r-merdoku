import json
import os
import re
from urllib.parse import quote

import httpx
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.models import TYPE_COLORS
from app.templates import templates

router = APIRouter()

ORACLE_PROMPT = """\
You are a Legend of the Five Rings CCG oracle assistant. Look up the L5R card "{query}" using the Oracle of the Void API.

API endpoint: POST https://api.oracleofthevoid.com/search
Required headers:
  accept: application/json, text/javascript, */*; q=0.01
  content-type: application/json
  origin: https://oracleofthevoid.com
  referer: https://oracleofthevoid.com/

Body (raw URL-encoded string):
  type_title=text&field_title={encoded_query}&table=l5r&sort=[{{"title.keyword":{{"order":"asc"}}}}]&size=10&from=0

The response is JSON with key path hits.hits[*]._source containing fields: title, clan, type, force, chi, cost, ph, startinghonor, keywords, text, legality, printing[].

Return ONLY a valid JSON object (no markdown, no explanation) in this format:
{{
  "title": "Card Name",
  "clan": "Clan Name",
  "type": "Personality|Holding|Strategy|Spell|Item|Region|Stronghold|Event",
  "cost": 0,
  "force": null,
  "chi": null,
  "ph": null,
  "startinghonor": null,
  "keywords": "keyword string",
  "text": "Card ability text",
  "flavor": "Flavor text or null",
  "set": "Set name",
  "rarity": "Common|Uncommon|Rare|Fixed"
}}

If you cannot fetch from the API, use your training knowledge of L5R CCG cards to provide accurate data. Never invent fictional cards — only return data for cards that actually exist.\
"""


async def _try_oracle_api(query: str) -> dict | None:
    body = (
        f"type_title=text&field_title={quote(query)}"
        f'&table=l5r&sort=[{{"title.keyword":{{"order":"asc"}}}}]&size=10&from=0'
    )
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.post(
                "https://api.oracleofthevoid.com/search",
                content=body.encode(),
                headers={
                    "accept": "application/json, text/javascript, */*; q=0.01",
                    "content-type": "application/json",
                    "origin": "https://oracleofthevoid.com",
                    "referer": "https://oracleofthevoid.com/",
                },
            )
        if resp.status_code != 200:
            return None
        hits = resp.json().get("hits", {}).get("hits", [])
        if not hits:
            return None
        src = hits[0]["_source"]
        return {
            "title": src.get("title", ""),
            "clan": src.get("clan", ""),
            "type": src.get("type", ""),
            "cost": src.get("cost", 0),
            "force": src.get("force"),
            "chi": src.get("chi"),
            "ph": src.get("ph"),
            "startinghonor": src.get("startinghonor"),
            "keywords": src.get("keywords", ""),
            "text": src.get("text", ""),
            "flavor": src.get("flavor"),
            "set": src.get("set", ""),
            "rarity": src.get("rarity", ""),
        }
    except Exception:
        return None


async def _try_claude(query: str) -> dict:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set — Oracle AI fallback unavailable.")

    import anthropic
    client = anthropic.AsyncAnthropic(api_key=api_key)
    message = await client.messages.create(
        model="claude-opus-4-5",
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": ORACLE_PROMPT.format(query=query, encoded_query=quote(query)),
        }],
    )
    raw = message.content[0].text
    match = re.search(r"\{[\s\S]+\}", raw)
    if not match:
        raise ValueError("Oracle returned no parseable card data.")
    return json.loads(match.group())


@router.post("/oracle/lookup", response_class=HTMLResponse)
async def oracle_lookup(request: Request):
    form = await request.form()
    query = (form.get("query") or "").strip()
    if not query:
        return HTMLResponse("")

    card = None
    error = None

    try:
        card = await _try_oracle_api(query)
        if card is None:
            card = await _try_claude(query)
    except Exception as exc:
        error = str(exc)

    return templates.TemplateResponse(request, "partials/oracle_result.html", {
        "card": card,
        "error": error,
        "type_colors": TYPE_COLORS,
    })
