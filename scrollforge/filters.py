import json
import random
import logging
from pathlib import Path
from functools import lru_cache

logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent

@lru_cache(maxsize=4)
def load_rules():
    path = BASE_DIR / 'data' / 'rules.json'
    with path.open('r', encoding='utf-8') as file:
        return json.load(file)

@lru_cache(maxsize=4)
def load_factions():
    path = BASE_DIR / 'data' / 'factions.json'
    with path.open('r', encoding='utf-8') as file:
        return json.load(file)

def is_valid_combo(race, faction, location, rules):
    race_name = race.get("name")
    faction_name = faction.get("name")
    location_name = location.get("name")

    # Invalid factions for race
    invalid_factions = rules.get("invalid_race_faction", {}).get(race_name, [])
    if faction_name in invalid_factions:
        return False

    # Invalid origins for race
    invalid_origins = rules.get("race_origin_restrictions", {}).get(race_name, [])
    if location_name in invalid_origins:
        return False

    return True

def filter_valid_factions(race, factions, rules):
    race_name = race.get("name")
    invalid_factions = set(rules.get("invalid_race_faction", {}).get(race_name, []))
    return [f for f in factions if f["name"] not in invalid_factions]

def filter_valid_origins(race, locations, rules):
    race_name = race.get("name")
    invalid_origins = set(rules.get("race_origin_restrictions", {}).get(race_name, []))
    return [l for l in locations if l["name"] not in invalid_origins]

def filter_valid_classes(race, classes, rules):
    race_name = race.get("name")
    restricted_classes = []
    for class_name, restricted_races in rules.get("class_restrictions", {}).items():
        if race_name in restricted_races:
            restricted_classes.append(class_name)
    return [c for c in classes if c["name"] not in restricted_classes]

def get_faction_relationships(faction_name, factions):
    """Extracts allies and rivals for a given faction from the faction data."""
    for f in factions:
        if f["name"] == faction_name:
            return {
                "allies": f.get("allies", []),
                "rivals": f.get("rivals", [])
            }
    logger.warning(f"Faction '{faction_name}' not found in data.")
    return {"allies": [], "rivals": []}

def get_race_allies_and_rivals(race, rules, factions):
    """Optional compatibility wrapper if you still want race-level ally/rival logic."""
    race_name = race.get("name")
    race_allies = rules.get("faction_relationships", {}).get("allies", {}).get(race_name, [])
    race_rivals = rules.get("faction_relationships", {}).get("rivals", {}).get(race_name, [])
    return {
        "allies": race_allies,
        "rivals": race_rivals
    }

def filter_deities_by_race(race, deities, rules):
    race_name = race.get("name")
    allowed = set(deity.lower() for deity in rules.get("preferred_deities", {}).get(race_name, []))
    return [d for d in deities if d.get("deity", "").lower() in allowed]

def filter_names_by_race(race, names_data):
    race_name = race.get("name")
    names = names_data.get(race_name)
    return names if names else ["Nameless Wanderer"]

def get_compatible_place(location, race, rules):
    # Hook for future location-level filtering (e.g., sub-place restrictions)
    return random.choice(location.get("major_places", [])) if location.get("major_places") else None
