"""Run once to populate merdoku.db from the original SAMPLE_DECK."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import engine, SessionLocal
from app.models import Base, Card

SAMPLE_DECK = [
    {"title": "Bayushi's Lies", "clan": "Scorpion", "type": "Stronghold", "cost": 0, "force": None, "chi": None, "ph": None, "startinghonor": 6, "keywords": "Scorpion", "text": "Bow: Give a Personality you control +2F until end of turn. Once per game: Search your deck for a Spell and put it into your hand.", "flavor": "Truth is the sharpest blade.", "set": "Scorpion Clan Coup", "rarity": "Fixed"},
    {"title": "Shosuro Furuyari", "clan": "Scorpion", "type": "Personality", "cost": 3, "force": 3, "chi": 4, "ph": 1, "keywords": "Shinobi Spy", "text": "Battle: Bow a target Personality in this battle with lower Chi than Furuyari's Chi. Furuyari is immune to Spells.", "flavor": "He vanishes like smoke, and returns like fire.", "set": "Gold Edition", "rarity": "Rare"},
    {"title": "Bayushi Kachiko", "clan": "Scorpion", "type": "Personality", "cost": 5, "force": 2, "chi": 7, "ph": 2, "keywords": "Imperial Favor", "text": "Political: Discard a card from your hand to give a target Personality -3 Chi until end of turn. If that Personality's Chi reaches 0, bow it.", "flavor": "A smile that cuts deeper than any blade.", "set": "Scorpion Clan Coup", "rarity": "Rare"},
    {"title": "Bayushi Tomaru", "clan": "Scorpion", "type": "Personality", "cost": 4, "force": 4, "chi": 3, "ph": 0, "keywords": "Bushi Duelist", "text": "Challenge: This duel is resolved as a Force duel instead of a Chi duel. If Tomaru wins a duel, straighten him.", "flavor": "He challenges without courtesy and wins without mercy.", "set": "Jade Edition", "rarity": "Uncommon"},
    {"title": "Shosuro Hametsu", "clan": "Scorpion", "type": "Personality", "cost": 2, "force": 2, "chi": 2, "ph": 1, "keywords": "Shinobi", "text": "Open: Pay 2 Gold to search your deck for a Spell card and add it to your hand.", "flavor": "Some knowledge should never leave the library.", "set": "Diamond Edition", "rarity": "Common"},
    {"title": "Bayushi Rikoji", "clan": "Scorpion", "type": "Personality", "cost": 3, "force": 2, "chi": 4, "ph": 1, "keywords": "Courtier Magistrate", "text": "Ceremony: Name a card. Your opponent reveals their hand; discard all copies of the named card.", "flavor": "A name spoken is power surrendered.", "set": "Lotus Edition", "rarity": "Rare"},
    {"title": "Soshi Seryoku", "clan": "Scorpion", "type": "Personality", "cost": 3, "force": 1, "chi": 5, "ph": 2, "keywords": "Shugenja Air", "text": "Spell: Fire Spell: Give this Personality +2 Chi this turn. After, you may cast a second Spell this turn at half cost.", "flavor": "The air carries whispers to those who know how to listen.", "set": "Emerald Edition", "rarity": "Uncommon"},
    {"title": "Soshi Yukio", "clan": "Scorpion", "type": "Personality", "cost": 2, "force": 1, "chi": 4, "ph": 1, "keywords": "Shugenja Air Void", "text": "Earth Spell: Sacrifice this Personality: Destroy a target Spell card in play.", "flavor": "She carries the silence of graves.", "set": "Shadowlands", "rarity": "Rare"},
    {"title": "Bayushi Tangen", "clan": "Scorpion", "type": "Personality", "cost": 4, "force": 3, "chi": 5, "ph": 1, "keywords": "Bushi Duelist Spy", "text": "Battle: Challenge a target Personality. The loser of the duel is dishonored. If dishonored Personality has 0 personal honor, send it home bowed.", "flavor": "He writes his duels in other men's blood.", "set": "Gold Edition", "rarity": "Rare"},
    {"title": "Shosuro Aroru", "clan": "Scorpion", "type": "Personality", "cost": 2, "force": 2, "chi": 3, "ph": 0, "keywords": "Shinobi Ninja", "text": "This Personality may move to battles as if it had Cavalry. Reaction: After a battle you win, draw a card.", "flavor": "The shadow moves faster than the man it follows.", "set": "Jade Edition", "rarity": "Common"},
    {"title": "Scorpion's Sting", "clan": "Scorpion", "type": "Holding", "cost": 2, "force": None, "chi": None, "ph": None, "keywords": "Dojo", "text": "Bow: Give a Shinobi Personality you control +2 Force until end of battle. You may use this ability during other players' turns.", "flavor": "Pain is the first lesson. Silence is the second.", "set": "Gold Edition", "rarity": "Uncommon"},
    {"title": "Shosuro Butei's Dojo", "clan": "Scorpion", "type": "Holding", "cost": 3, "force": None, "chi": None, "ph": None, "keywords": "Dojo Shadowlands", "text": "Bow: Search your deck for a Shinobi Personality with cost 3 or less and put it into play. That Personality comes into play bowed.", "flavor": "The greatest assassins learn in the dark.", "set": "Emerald Edition", "rarity": "Rare"},
    {"title": "The Shadowed Tower", "clan": "Scorpion", "type": "Holding", "cost": 4, "force": None, "chi": None, "ph": None, "keywords": "Castle Library", "text": "Each of your Shugenja gains +1 Chi. Bow: Look at target opponent's hand.", "flavor": "Every secret has a price. Knowledge of it costs more.", "set": "Diamond Edition", "rarity": "Rare"},
    {"title": "False Loyalties", "clan": "Scorpion", "type": "Holding", "cost": 2, "force": None, "chi": None, "ph": None, "keywords": "Market", "text": "Bow: Take control of target Personality with personal honor 0 until end of turn. Use this ability only during battle.", "flavor": "Loyalty bought is loyalty owned.", "set": "Lotus Edition", "rarity": "Uncommon"},
    {"title": "Hidden Blade", "clan": "Scorpion", "type": "Item", "cost": 1, "force": None, "chi": None, "ph": None, "keywords": "Weapon Knife", "text": "Force +1. Bow attached Personality: Give a target Personality -1 Force until end of turn. This ability may only be used once per turn.", "flavor": "The knife you do not see is the one that kills you.", "set": "Gold Edition", "rarity": "Common"},
    {"title": "Kolat Master's Cloak", "clan": "Scorpion", "type": "Item", "cost": 2, "force": None, "chi": None, "ph": None, "keywords": "Armor Kolat", "text": "Bow: Prevent all non-Ninja Personalities from targeting bearer until end of phase. Reaction: After bearer is challenged, cancel the duel.", "flavor": "In the shadows, rank has no meaning.", "set": "Jade Edition", "rarity": "Rare"},
    {"title": "Mask of the Oni", "clan": "Scorpion", "type": "Item", "cost": 3, "force": None, "chi": None, "ph": None, "keywords": "Mask Shadowlands", "text": "Force +2, Chi -1. Bearer is immune to Fear effects. Bow: Give target Personality Fear 3 until end of turn.", "flavor": "When you look into the mask, the mask looks back.", "set": "Shadowlands", "rarity": "Rare"},
    {"title": "Whispers of Shadow", "clan": "Scorpion", "type": "Spell", "cost": 2, "force": None, "chi": None, "ph": None, "keywords": "Air Void Illusion", "text": "Give a target Personality -3 Chi until end of turn. If their Chi drops to 0, bow them.", "flavor": "Truth bends when the wind speaks falsely.", "set": "Emerald Edition", "rarity": "Uncommon"},
    {"title": "Mark of the Ninja", "clan": "Scorpion", "type": "Spell", "cost": 1, "force": None, "chi": None, "ph": None, "keywords": "Air Void", "text": "Give target Personality the Ninja keyword until end of turn. Ninja Personalities may not be targeted by non-Ninja abilities.", "flavor": "Identity is the first disguise.", "set": "Gold Edition", "rarity": "Common"},
    {"title": "Sinister Satisfaction", "clan": "Scorpion", "type": "Spell", "cost": 3, "force": None, "chi": None, "ph": None, "keywords": "Void Curse", "text": "Give target Personality -2 Force and -2 Chi until end of turn. If that Personality is dishonored, destroy it instead.", "flavor": "Shame is a slow blade.", "set": "Diamond Edition", "rarity": "Uncommon"},
    {"title": "Web of Lies", "clan": "Scorpion", "type": "Strategy", "cost": 0, "force": None, "chi": None, "ph": None, "keywords": "Tactic", "text": "Battle: Discard target Personality's attachment. Then dishonor that Personality.", "flavor": "Strip away the armor. Strip away the name.", "set": "Gold Edition", "rarity": "Uncommon"},
    {"title": "Blackmail", "clan": "Scorpion", "type": "Strategy", "cost": 1, "force": None, "chi": None, "ph": None, "keywords": "Political", "text": "Political: Choose a Personality. Your opponent must discard a card from their hand or bow that Personality.", "flavor": "Everyone has something to hide.", "set": "Jade Edition", "rarity": "Common"},
    {"title": "Sudden Movement", "clan": "Scorpion", "type": "Strategy", "cost": 0, "force": None, "chi": None, "ph": None, "keywords": "Tactic Cavalry", "text": "Battle: Move a Personality from your home into this battle. That Personality may act this turn.", "flavor": "Strike before they count your shadows.", "set": "Lotus Edition", "rarity": "Common"},
    {"title": "The Price of Failure", "clan": "Scorpion", "type": "Strategy", "cost": 2, "force": None, "chi": None, "ph": None, "keywords": "Honor Politics", "text": "Discard a Personality you control: Lose 1 honor and give target opponent's Personality -3 Force until end of turn.", "flavor": "Every pawn has a final use.", "set": "Emerald Edition", "rarity": "Uncommon"},
    {"title": "Cunning Maneuver", "clan": "Scorpion", "type": "Strategy", "cost": 0, "force": None, "chi": None, "ph": None, "keywords": "Tactic", "text": "Battle: Redirect a battle action targeting your Personality to another valid target.", "flavor": "The battlefield is a stage, and the general a playwright.", "set": "Diamond Edition", "rarity": "Common"},
    {"title": "Cut the Threads", "clan": "Scorpion", "type": "Strategy", "cost": 1, "force": None, "chi": None, "ph": None, "keywords": "Tactic", "text": "Destroy target Follower in this battle. If no Follower is present, give target Personality -1 Force until end of battle.", "flavor": "An army is only as strong as its weakest tie.", "set": "Gold Edition", "rarity": "Common"},
    {"title": "A Soldier's Lie", "clan": "Scorpion", "type": "Strategy", "cost": 1, "force": None, "chi": None, "ph": None, "keywords": "Political Illusion", "text": "Cancel the effects of a target Strategy card. Draw a card.", "flavor": "The best lie is the one they want to believe.", "set": "Jade Edition", "rarity": "Uncommon"},
    {"title": "Poison Tongue", "clan": "Scorpion", "type": "Strategy", "cost": 2, "force": None, "chi": None, "ph": None, "keywords": "Political Poison", "text": "Dishonor target Personality. That Personality gets -2 Chi until they straighten.", "flavor": "Words leave no marks that courts can see.", "set": "Lotus Edition", "rarity": "Common"},
    {"title": "Ruthless Tactics", "clan": "Scorpion", "type": "Strategy", "cost": 1, "force": None, "chi": None, "ph": None, "keywords": "Tactic", "text": "Battle: Give all your Personalities in this battle +1 Force this turn. Lose 1 honor.", "flavor": "Victory without cost is victory without meaning.", "set": "Emerald Edition", "rarity": "Common"},
    {"title": "Enemy's Weakness", "clan": "Scorpion", "type": "Strategy", "cost": 2, "force": None, "chi": None, "ph": None, "keywords": "Tactic Spy", "text": "Look at target opponent's hand. Choose a card; they must discard it.", "flavor": "Knowledge of weakness is the greatest weapon.", "set": "Diamond Edition", "rarity": "Uncommon"},
    {"title": "Silent Ambush", "clan": "Scorpion", "type": "Strategy", "cost": 0, "force": None, "chi": None, "ph": None, "keywords": "Tactic Ninja", "text": "Battle: Move a Ninja Personality from your home into this battle before battle resolution.", "flavor": "They do not see us until it is too late.", "set": "Gold Edition", "rarity": "Common"},
    {"title": "Shosuro Shinobi", "clan": "Scorpion", "type": "Personality", "cost": 2, "force": 2, "chi": 2, "ph": 0, "keywords": "Shinobi Ninja", "text": "This Personality may not be targeted by enemy Personalities during battles unless they have the Ninja keyword.", "flavor": "His name is an alias. His face is a mask.", "set": "Jade Edition", "rarity": "Common"},
    {"title": "Bayushi Gensato", "clan": "Scorpion", "type": "Personality", "cost": 3, "force": 3, "chi": 3, "ph": 1, "keywords": "Bushi", "text": "Battle: Bow: Give a target Personality you control +2 Force until end of battle.", "flavor": "The blade serves, until the hand is cut.", "set": "Emerald Edition", "rarity": "Common"},
    {"title": "Bayushi Paneki", "clan": "Scorpion", "type": "Personality", "cost": 6, "force": 5, "chi": 6, "ph": 2, "keywords": "Champion Bushi Duelist", "text": "Forced Reaction: After Paneki enters play, your opponent loses 2 honor. Battle: Challenge a target Personality. Add +3 to Paneki's total in this duel.", "flavor": "The clan champion need not whisper. His reputation speaks first.", "set": "Gold Edition", "rarity": "Rare"},
    {"title": "Soshi Kitaro", "clan": "Scorpion", "type": "Personality", "cost": 3, "force": 2, "chi": 4, "ph": 1, "keywords": "Shugenja Air", "text": "Air Spell: Discard a card from your hand: Draw two cards.", "flavor": "Knowledge is the water that fills the cup of power.", "set": "Diamond Edition", "rarity": "Uncommon"},
    {"title": "Bayushi Yojiro", "clan": "Scorpion", "type": "Personality", "cost": 4, "force": 2, "chi": 6, "ph": 3, "keywords": "Magistrate Courtier Spy", "text": "Political: Name a card. Your opponent reveals their hand. Discard all copies of the named card. Gain 1 honor.", "flavor": "He is the only honest Scorpion, and therefore the most dangerous.", "set": "Jade Edition", "rarity": "Rare"},
    {"title": "A Shaded Garden", "clan": "Scorpion", "type": "Holding", "cost": 2, "force": None, "chi": None, "ph": None, "keywords": "Garden", "text": "Bow: Gain 1 honor. Bow: Give target Personality +1 Chi until end of turn.", "flavor": "Even scorpions need beauty.", "set": "Lotus Edition", "rarity": "Common"},
    {"title": "The Path of Whispers", "clan": "Scorpion", "type": "Region", "cost": 3, "force": None, "chi": None, "ph": None, "keywords": "Region", "text": "Each Shinobi Personality you control may move as if they had Cavalry. Once per turn, bow this Region: Reveal the top card of target opponent's deck.", "flavor": "All roads lead somewhere. Most lead here first.", "set": "Emerald Edition", "rarity": "Rare"},
    {"title": "Night Raid", "clan": "Scorpion", "type": "Strategy", "cost": 0, "force": None, "chi": None, "ph": None, "keywords": "Tactic Ninja", "text": "Battle: Bow target Holding at the battle location.", "flavor": "What the Scorpion takes, the Scorpion keeps.", "set": "Gold Edition", "rarity": "Common"},
    {"title": "Bayushi Aramoro", "clan": "Scorpion", "type": "Personality", "cost": 4, "force": 4, "chi": 3, "ph": 1, "keywords": "Bushi Duelist Ninja", "text": "Battle: Challenge a target Personality. If Aramoro wins, that Personality is removed from the game.", "flavor": "He does not defeat his opponents. He erases them.", "set": "Jade Edition", "rarity": "Rare"},
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        for data in SAMPLE_DECK:
            existing = db.query(Card).filter(Card.title == data["title"]).first()
            if existing:
                continue
            card = Card(
                title=data["title"],
                clan=data["clan"],
                type=data["type"],
                cost=data.get("cost", 0) or 0,
                force=data.get("force"),
                chi=data.get("chi"),
                ph=data.get("ph"),
                startinghonor=data.get("startinghonor"),
                keywords=data.get("keywords"),
                text=data.get("text"),
                flavor=data.get("flavor"),
                set_name=data.get("set"),
                rarity=data.get("rarity"),
            )
            db.add(card)
        db.commit()
        count = db.query(Card).count()
        print(f"Seeded: {count} cards in database.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
