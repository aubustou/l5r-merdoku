from urllib.parse import unquote
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Card, TYPE_COLORS, CARD_TYPE_ORDER
from app.templates import templates

router = APIRouter()


def _compute_stats(cards: list) -> dict:
    type_counts: dict[str, int] = {}
    for c in cards:
        type_counts[c.type] = type_counts.get(c.type, 0) + 1

    costed = [c for c in cards if c.cost > 0]
    avg_cost = f"{sum(c.cost for c in costed) / len(costed):.1f}" if costed else "—"

    personalities = [c for c in cards if c.type == "Personality"]
    avg_force = (
        f"{sum(c.force or 0 for c in personalities) / len(personalities):.1f}"
        if personalities else "—"
    )

    cost_curve = {cost: len([c for c in cards if c.cost == cost]) for cost in range(7)}
    max_curve = max(cost_curve.values(), default=1)

    return {
        "type_counts": type_counts,
        "avg_cost": avg_cost,
        "avg_force": avg_force,
        "cost_curve": cost_curve,
        "max_curve": max_curve,
    }


def _query_cards(
    db: Session,
    filter: str = "All",
    search: str = "",
    sort_by: str = "type",
) -> list:
    query = db.query(Card)
    if filter and filter != "All":
        query = query.filter(Card.type == filter)
    if search:
        query = query.filter(
            Card.title.ilike(f"%{search}%") | Card.text.ilike(f"%{search}%")
        )
    cards = query.all()

    if sort_by == "name":
        cards.sort(key=lambda c: c.title)
    elif sort_by == "cost":
        cards.sort(key=lambda c: c.cost)
    elif sort_by == "force":
        cards.sort(key=lambda c: -(c.force or 0))
    elif sort_by == "chi":
        cards.sort(key=lambda c: -(c.chi or 0))
    else:
        order = {t: i for i, t in enumerate(CARD_TYPE_ORDER)}
        cards.sort(key=lambda c: (order.get(c.type, 99), c.title))

    return cards


def _group(cards: list) -> dict:
    grouped: dict[str, list] = {}
    for c in cards:
        grouped.setdefault(c.type, []).append(c)
    return grouped


@router.get("/", response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db)):
    cards = _query_cards(db)
    stronghold = next((c for c in cards if c.type == "Stronghold"), None)
    starting_honor = stronghold.startinghonor if stronghold else 6

    return templates.TemplateResponse(request, "index.html", {
        "cards": cards,
        "grouped": _group(cards),
        "type_order": CARD_TYPE_ORDER,
        "type_colors": TYPE_COLORS,
        "total": len(cards),
        "starting_honor": starting_honor,
        "filter": "All",
        "search": "",
        "sort_by": "type",
        "is_htmx": False,
        **_compute_stats(cards),
    })


@router.get("/cards/grid", response_class=HTMLResponse)
async def cards_grid(
    request: Request,
    filter: str = "All",
    search: str = "",
    sort_by: str = "type",
    db: Session = Depends(get_db),
):
    cards = _query_cards(db, filter, search, sort_by)

    return templates.TemplateResponse(request, "partials/card_grid.html", {
        "cards": cards,
        "grouped": _group(cards),
        "type_order": CARD_TYPE_ORDER,
        "type_colors": TYPE_COLORS,
        "total": len(cards),
        "filter": filter,
        "is_htmx": True,
        **_compute_stats(cards),
    })


@router.get("/cards/{title}/detail", response_class=HTMLResponse)
async def card_detail(request: Request, title: str, db: Session = Depends(get_db)):
    card = db.query(Card).filter(Card.title == unquote(title)).first()
    if not card:
        return HTMLResponse("<p style='color:var(--outline);padding:16px'>Card not found.</p>", status_code=404)
    return templates.TemplateResponse(request, "partials/card_detail.html", {
        "card": card,
        "type_colors": TYPE_COLORS,
    })


@router.post("/cards/add", response_class=HTMLResponse)
async def add_card(request: Request, db: Session = Depends(get_db)):
    form = await request.form()

    def _int(key):
        v = form.get(key, "")
        return int(v) if v else None

    if not db.query(Card).filter(Card.title == form.get("title")).first():
        db.add(Card(
            title=form.get("title", ""),
            clan=form.get("clan", ""),
            type=form.get("type", ""),
            cost=_int("cost") or 0,
            force=_int("force"),
            chi=_int("chi"),
            ph=_int("ph"),
            startinghonor=_int("startinghonor"),
            keywords=form.get("keywords") or None,
            text=form.get("text") or None,
            flavor=form.get("flavor") or None,
            set_name=form.get("set") or None,
            rarity=form.get("rarity") or None,
        ))
        db.commit()

    response = HTMLResponse("", status_code=204)
    response.headers["HX-Trigger"] = "cardsChanged"
    return response
