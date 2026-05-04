import os
import threading
import time

import httpx
import pytest
import uvicorn
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

TEST_DATABASE_URL = "sqlite:///./test_merdoku.db"
TEST_PORT = 8791

_SEED_CARDS = [
    dict(
        title="Bayushi Yojiro",
        clan="Scorpion",
        type="Personality",
        cost=4,
        force=3,
        chi=3,
        ph=2,
        keywords="Samurai Duelist",
        text="Bow: target personality loses a keyword.",
        set_name="Imperial",
        rarity="Rare",
    ),
    dict(
        title="Shosuro Adori",
        clan="Scorpion",
        type="Personality",
        cost=3,
        force=2,
        chi=4,
        ph=1,
        keywords="Samurai",
        text="Sneak Attack.",
        set_name="Imperial",
        rarity="Uncommon",
    ),
    dict(
        title="Iron Mine",
        clan="Scorpion",
        type="Holding",
        cost=0,
        text="Produce 2 gold.",
        set_name="Imperial",
        rarity="Common",
    ),
    dict(
        title="Biting Steel",
        clan="Scorpion",
        type="Strategy",
        cost=2,
        text="Deal 3 force to target.",
        set_name="Imperial",
        rarity="Common",
    ),
    dict(
        title="Beiden Pass",
        clan="Scorpion",
        type="Stronghold",
        cost=0,
        startinghonor=6,
        set_name="Imperial",
        rarity="Fixed",
    ),
]


def _seed_database(Session):
    from app.models import Card

    db = Session()
    try:
        for data in _SEED_CARDS:
            if not db.query(Card).filter(Card.title == data["title"]).first():
                db.add(Card(**data))
        db.commit()
    finally:
        db.close()


@pytest.fixture(scope="session")
def live_server():
    from app.database import Base, get_db
    from app.main import app

    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    _seed_database(TestSession)

    def _get_test_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _get_test_db

    config = uvicorn.Config(app, host="127.0.0.1", port=TEST_PORT, log_level="error")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    for _ in range(30):
        try:
            httpx.get(f"http://127.0.0.1:{TEST_PORT}/", timeout=1.0)
            break
        except Exception:
            time.sleep(0.2)

    yield f"http://127.0.0.1:{TEST_PORT}"

    server.should_exit = True
    thread.join(timeout=5)
    app.dependency_overrides.clear()
    engine.dispose()
    try:
        os.unlink("test_merdoku.db")
    except FileNotFoundError:
        pass


@pytest.fixture(scope="session")
def base_url(live_server):
    return live_server
