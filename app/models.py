from sqlalchemy import Column, Integer, String, Text
from app.database import Base

CLAN_COLORS = {
    "Crab":        {"border": "#5b7fa6", "glow": "rgba(91,127,166,0.3)"},
    "Crane":       {"border": "#a8c8e8", "glow": "rgba(168,200,232,0.3)"},
    "Dragon":      {"border": "#6db88a", "glow": "rgba(109,184,138,0.3)"},
    "Lion":        {"border": "#e8c84a", "glow": "rgba(232,200,74,0.3)"},
    "Mantis":      {"border": "#d4a840", "glow": "rgba(212,168,64,0.3)"},
    "Phoenix":     {"border": "#e87840", "glow": "rgba(232,120,64,0.3)"},
    "Scorpion":    {"border": "#c84848", "glow": "rgba(200,72,72,0.3)"},
    "Unicorn":     {"border": "#b880d0", "glow": "rgba(184,128,208,0.3)"},
    "Shadowlands": {"border": "#606060", "glow": "rgba(96,96,96,0.3)"},
    "Naga":        {"border": "#78b878", "glow": "rgba(120,184,120,0.3)"},
    "Imperial":    {"border": "#d0a840", "glow": "rgba(208,168,64,0.3)"},
    "default":     {"border": "#c9a84c", "glow": "rgba(201,168,76,0.3)"},
}

TYPE_COLORS = {
    "Personality": "#ffb3ad",
    "Holding":     "#adcfb3",
    "Strategy":    "#eebd8e",
    "Spell":       "#b8c8e8",
    "Item":        "#d4b888",
    "Region":      "#98c898",
    "Stronghold":  "#c9a84c",
    "Event":       "#d888b8",
}

CARD_TYPE_ORDER = [
    "Stronghold", "Personality", "Holding", "Item",
    "Spell", "Strategy", "Region", "Event",
]

LIGHTS = [
    {"filter": "sepia(0.3) saturate(1.1) brightness(0.88) contrast(1.08)",          "object_position": "50% 20%"},
    {"filter": "sepia(0.1) saturate(0.85) brightness(0.82) hue-rotate(200deg) contrast(1.12)", "object_position": "50% 15%"},
    {"filter": "brightness(0.72) contrast(1.25) saturate(1.2)",                       "object_position": "40% 25%"},
    {"filter": "sepia(0.4) saturate(1.3) brightness(0.85) hue-rotate(-10deg)",        "object_position": "60% 10%"},
    {"filter": "saturate(0.7) brightness(0.92) contrast(0.95)",                       "object_position": "50% 30%"},
    {"filter": "brightness(0.65) saturate(1.4) contrast(1.3) hue-rotate(10deg)",      "object_position": "45% 20%"},
]


class Card(Base):
    __tablename__ = "cards"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    title         = Column(String, nullable=False, unique=True, index=True)
    clan          = Column(String, nullable=False, index=True)
    type          = Column(String, nullable=False, index=True)
    cost          = Column(Integer, nullable=False, default=0)
    force         = Column(Integer, nullable=True)
    chi           = Column(Integer, nullable=True)
    ph            = Column(Integer, nullable=True)
    startinghonor = Column(Integer, nullable=True)
    keywords      = Column(String, nullable=True)
    text          = Column(Text, nullable=True)
    flavor        = Column(Text, nullable=True)
    set_name      = Column(String, nullable=True)
    rarity        = Column(String, nullable=True)
