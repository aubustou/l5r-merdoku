"""Playwright end-to-end tests for the Merdoku L5R deck browser."""
from unittest.mock import AsyncMock, patch

import pytest
from playwright.sync_api import Page, expect


# ---------------------------------------------------------------------------
# Homepage
# ---------------------------------------------------------------------------

def test_homepage_loads(page: Page, base_url: str):
    page.goto(base_url)
    expect(page).to_have_title("Merdoku — Relic & Ritual")
    expect(page.locator(".card-tile")).not_to_have_count(0)


def test_homepage_shows_header(page: Page, base_url: str):
    page.goto(base_url)
    expect(page.locator(".header-title")).to_have_text("Merdoku")
    # Beiden Pass stronghold sets starting honor to 6
    expect(page.locator(".honor-value")).to_have_text("6")


def test_homepage_shows_all_seeded_cards(page: Page, base_url: str):
    page.goto(base_url)
    for title in ("Bayushi Yojiro", "Shosuro Adori", "Iron Mine", "Biting Steel", "Beiden Pass"):
        expect(page.locator(".card-tile").filter(has_text=title)).to_be_visible()


# ---------------------------------------------------------------------------
# Type filter
# ---------------------------------------------------------------------------

def test_filter_personality(page: Page, base_url: str):
    page.goto(base_url)
    page.locator(".type-btn", has_text="Personality").click()
    expect(page.locator(".card-tile").filter(has_text="Bayushi Yojiro")).to_be_visible()
    expect(page.locator(".card-tile").filter(has_text="Shosuro Adori")).to_be_visible()
    expect(page.locator(".card-tile").filter(has_text="Iron Mine")).to_have_count(0)
    expect(page.locator(".card-tile").filter(has_text="Biting Steel")).to_have_count(0)


def test_filter_holding(page: Page, base_url: str):
    page.goto(base_url)
    page.locator(".type-btn", has_text="Holding").click()
    expect(page.locator(".card-tile").filter(has_text="Iron Mine")).to_be_visible()
    expect(page.locator(".card-tile").filter(has_text="Bayushi Yojiro")).to_have_count(0)


def test_filter_strategy(page: Page, base_url: str):
    page.goto(base_url)
    page.locator(".type-btn", has_text="Strategy").click()
    expect(page.locator(".card-tile").filter(has_text="Biting Steel")).to_be_visible()
    expect(page.locator(".card-tile").filter(has_text="Bayushi Yojiro")).to_have_count(0)


def test_filter_all_resets_after_type_filter(page: Page, base_url: str):
    page.goto(base_url)
    page.locator(".type-btn", has_text="Personality").click()
    expect(page.locator(".card-tile").filter(has_text="Iron Mine")).to_have_count(0)
    page.locator(".type-btn", has_text="All").click()
    expect(page.locator(".card-tile").filter(has_text="Iron Mine")).to_be_visible()
    expect(page.locator(".card-tile").filter(has_text="Bayushi Yojiro")).to_be_visible()


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

def test_search_by_title(page: Page, base_url: str):
    page.goto(base_url)
    page.locator(".search-input").fill("Bayushi")
    page.wait_for_timeout(350)  # 300 ms debounce + buffer
    expect(page.locator(".card-tile").filter(has_text="Bayushi Yojiro")).to_be_visible()
    expect(page.locator(".card-tile").filter(has_text="Iron Mine")).to_have_count(0)


def test_search_by_card_text(page: Page, base_url: str):
    page.goto(base_url)
    page.locator(".search-input").fill("Produce 2 gold")
    page.wait_for_timeout(350)
    expect(page.locator(".card-tile").filter(has_text="Iron Mine")).to_be_visible()
    expect(page.locator(".card-tile").filter(has_text="Bayushi Yojiro")).to_have_count(0)


def test_search_no_results_shows_empty_state(page: Page, base_url: str):
    page.goto(base_url)
    page.locator(".search-input").fill("zzz_no_such_card_xyz")
    page.wait_for_timeout(350)
    expect(page.locator(".gallery-empty")).to_be_visible()


def test_clearing_search_restores_cards(page: Page, base_url: str):
    page.goto(base_url)
    page.locator(".search-input").fill("zzz_no_such_card_xyz")
    page.wait_for_timeout(350)
    expect(page.locator(".gallery-empty")).to_be_visible()
    page.locator(".search-input").fill("")
    page.wait_for_timeout(350)
    expect(page.locator(".card-tile").filter(has_text="Bayushi Yojiro")).to_be_visible()


# ---------------------------------------------------------------------------
# Sort
# ---------------------------------------------------------------------------

def test_sort_by_name_alphabetical(page: Page, base_url: str):
    # Cards are grouped by type; sort=name orders cards within each section alphabetically.
    page.goto(base_url)
    page.locator(".sort-select").select_option("name")
    page.wait_for_selector("#card-grid .card-tile")
    # Check that within the Personality section, Bayushi Yojiro precedes Shosuro Adori
    personality_tiles = page.locator(".card-section").filter(
        has=page.locator(".section-label", has_text="Personalitys")
    ).locator(".card-title").all_text_contents()
    assert personality_tiles == sorted(personality_tiles), (
        f"Personality cards not sorted alphabetically: {personality_tiles}"
    )


def test_sort_by_cost_ascending(page: Page, base_url: str):
    # Cards are grouped by type; sort=cost orders cards within each section by cost.
    page.goto(base_url)
    page.locator(".sort-select").select_option("cost")
    page.wait_for_selector("#card-grid .card-tile")
    # Within the Personality section: Shosuro Adori (cost 3) before Bayushi Yojiro (cost 4)
    personality_section = page.locator(".card-section").filter(
        has=page.locator(".section-label", has_text="Personalitys")
    )
    personality_titles = personality_section.locator(".card-title").all_text_contents()
    assert personality_titles.index("Shosuro Adori") < personality_titles.index("Bayushi Yojiro"), (
        f"Personality cards not sorted by cost ascending: {personality_titles}"
    )


# ---------------------------------------------------------------------------
# Card detail modal
# ---------------------------------------------------------------------------

def test_card_detail_modal_opens(page: Page, base_url: str):
    page.goto(base_url)
    page.locator(".card-tile").filter(has_text="Bayushi Yojiro").click()
    expect(page.locator(".modal-backdrop")).to_be_visible()
    expect(page.locator(".modal-title-name")).to_have_text("Bayushi Yojiro")


def test_card_detail_shows_clan_and_type(page: Page, base_url: str):
    page.goto(base_url)
    page.locator(".card-tile").filter(has_text="Bayushi Yojiro").click()
    expect(page.locator(".modal-backdrop")).to_be_visible()
    modal = page.locator(".modal-card")
    expect(modal.locator(".clan-badge")).to_have_text("Scorpion")
    expect(modal.locator(".type-badge")).to_have_text("Personality")


def test_card_detail_modal_closes_with_button(page: Page, base_url: str):
    page.goto(base_url)
    page.locator(".card-tile").filter(has_text="Bayushi Yojiro").click()
    expect(page.locator(".modal-backdrop")).to_be_visible()
    page.locator(".modal-close-btn").click()
    expect(page.locator("#modal-container")).to_be_empty()


def test_card_detail_modal_closes_with_escape(page: Page, base_url: str):
    page.goto(base_url)
    page.locator(".card-tile").filter(has_text="Bayushi Yojiro").click()
    expect(page.locator(".modal-backdrop")).to_be_visible()
    page.keyboard.press("Escape")
    expect(page.locator("#modal-container")).to_be_empty()


def test_card_detail_modal_closes_on_backdrop_click(page: Page, base_url: str):
    page.goto(base_url)
    page.locator(".card-tile").filter(has_text="Bayushi Yojiro").click()
    expect(page.locator(".modal-backdrop")).to_be_visible()
    page.locator(".modal-backdrop").click(position={"x": 5, "y": 5})
    expect(page.locator("#modal-container")).to_be_empty()


def test_card_detail_tab_switching(page: Page, base_url: str):
    page.goto(base_url)
    page.locator(".card-tile").filter(has_text="Bayushi Yojiro").click()
    expect(page.locator(".modal-backdrop")).to_be_visible()

    # Text tab is active by default
    expect(page.locator(".tab-panel[data-panel='text']")).to_be_visible()

    # Switch to Keywords tab
    page.locator(".tab-btn", has_text="Keywords").click()
    expect(page.locator(".tab-panel[data-panel='keywords']")).to_be_visible()
    expect(page.locator(".tab-panel[data-panel='text']")).to_be_hidden()

    # Switch to Lore tab
    page.locator(".tab-btn", has_text="Lore").click()
    expect(page.locator(".tab-panel[data-panel='lore']")).to_be_visible()
    expect(page.locator(".tab-panel[data-panel='keywords']")).to_be_hidden()


# ---------------------------------------------------------------------------
# Oracle lookup
# ---------------------------------------------------------------------------

_MOCK_ORACLE_CARD = {
    "title": "Bayushi Kachiko",
    "clan": "Scorpion",
    "type": "Personality",
    "cost": 5,
    "force": 3,
    "chi": 5,
    "ph": 2,
    "startinghonor": None,
    "keywords": "Samurai Magistrate",
    "text": "Political action: bow target personality.",
    "flavor": None,
    "set": "Imperial",
    "rarity": "Rare",
}


def test_oracle_lookup_displays_result(page: Page, base_url: str):
    with patch(
        "app.routers.oracle._try_oracle_api",
        new=AsyncMock(return_value=_MOCK_ORACLE_CARD),
    ):
        page.goto(base_url)
        page.locator(".oracle-input").fill("Bayushi Kachiko")
        page.locator("#oracle-seek-btn").click()
        expect(page.locator(".oracle-card-preview")).to_be_visible(timeout=6000)
        expect(page.locator(".oracle-card-title")).to_have_text("Bayushi Kachiko")


def test_oracle_lookup_shows_clan_and_type(page: Page, base_url: str):
    with patch(
        "app.routers.oracle._try_oracle_api",
        new=AsyncMock(return_value=_MOCK_ORACLE_CARD),
    ):
        page.goto(base_url)
        page.locator(".oracle-input").fill("Bayushi Kachiko")
        page.locator("#oracle-seek-btn").click()
        expect(page.locator(".oracle-card-preview")).to_be_visible(timeout=6000)
        preview = page.locator(".oracle-card-preview")
        expect(preview.locator(".clan-badge")).to_have_text("Scorpion")
        expect(preview.locator(".type-badge")).to_have_text("Personality")


def test_oracle_lookup_empty_query_returns_nothing(page: Page, base_url: str):
    page.goto(base_url)
    page.locator("#oracle-seek-btn").click()
    # Result area should stay empty when no query is submitted
    expect(page.locator("#oracle-result")).to_be_empty()


def test_oracle_lookup_error_displays_message(page: Page, base_url: str):
    with patch(
        "app.routers.oracle._try_oracle_api",
        new=AsyncMock(return_value=None),
    ), patch(
        "app.routers.oracle._try_claude",
        new=AsyncMock(side_effect=ValueError("ANTHROPIC_API_KEY not set")),
    ):
        page.goto(base_url)
        page.locator(".oracle-input").fill("Some Card")
        page.locator("#oracle-seek-btn").click()
        expect(page.locator(".oracle-error")).to_be_visible(timeout=6000)


def test_oracle_add_to_gallery(page: Page, base_url: str):
    unique_card = {**_MOCK_ORACLE_CARD, "title": "Bayushi Aramoro"}
    with patch(
        "app.routers.oracle._try_oracle_api",
        new=AsyncMock(return_value=unique_card),
    ):
        page.goto(base_url)
        page.locator(".oracle-input").fill("Bayushi Aramoro")
        page.locator("#oracle-seek-btn").click()
        expect(page.locator(".oracle-card-preview")).to_be_visible(timeout=6000)

        initial_count = page.locator(".card-tile").count()
        page.locator(".oracle-add-btn").click()

        # Oracle result area shows the "Added" confirmation
        expect(page.locator(".oracle-added")).to_be_visible(timeout=6000)
        # Card grid refreshes via cardsChanged HX-Trigger
        expect(page.locator(".card-tile")).to_have_count(initial_count + 1, timeout=6000)
