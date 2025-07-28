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

    # Check if faction is preferred for the race
    preferred_factions = rules.get("preferred_race_factions", {}).get(race_name, [])
    if preferred_factions and faction_name not in preferred_factions:
        return False

    # Check if location is preferred for the race
    preferred_origins = rules.get("preferred_race_origin", {}).get(race_name, [])
    if preferred_origins and location_name not in preferred_origins:
        return False

    return True


def filter_valid_factions(race, factions, rules):
    race_name = race.get("name")
    preferred_factions = set(rules.get("preferred_race_factions", {}).get(race_name, []))
    if preferred_factions:
        return [f for f in factions if f["name"] in preferred_factions]
    return factions


def filter_valid_origins(race, locations, rules):
    race_name = race.get("name")
    preferred_origins = set(rules.get("preferred_race_origin", {}).get(race_name, []))
    if preferred_origins:
        return [l for l in locations if l["name"] in preferred_origins]
    return locations


def filter_valid_classes(race, classes, rules):
    race_name = race.get("name")
    preferred_classes = rules.get("preferred_race_class", {}).get(race_name, [])
    if preferred_classes:
        return [c for c in classes if c["name"] in preferred_classes]
    return classes


def filter_deities_by_race(race, deities, rules):
    race_name = race.get("name")
    allowed = set(deity.lower() for deity in rules.get("preferred_race_deities", {}).get(race_name, []))
    return [d for d in deities if d.get("deity", "").lower() in allowed]


def filter_names_by_race(race, names_data):
    race_name = race.get("name")
    names = names_data.get(race_name, [])
    return names if names else ["Nameless Wanderer"]


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


def get_valid_faction_candidates(race, char_class, factions, rules):
    race_name = race.get("name")
    class_name = char_class.get("name")

    class_allowed = set(rules.get("preferred_class_factions", {}).get(class_name, []))
    race_preferred = set(rules.get("preferred_race_factions", {}).get(race_name, []))

    if race_preferred:
        return [f for f in factions if f["name"] in class_allowed and f["name"] in race_preferred]
    return [f for f in factions if f["name"] in class_allowed]


def is_faction_conflicted(faction_name, selected_factions):
    return faction_name in selected_factions


def select_faction(race, char_class, factions, rules, override_faction_name=None):
    candidates = get_valid_faction_candidates(race, char_class, factions, rules)

    if override_faction_name:
        override = next((f for f in factions if f["name"] == override_faction_name), None)
        if override:
            return override

    if not candidates:
        # Optional: Log a warning for debugging
        logger.warning(f"No valid faction candidates found for race {race['name']} and class {char_class['name']}")
        return {
            "name": "Unaffiliated",
            "description": "A lone wanderer with no faction ties.",
            "symbol": "⚪",
            "neutral": True
        }

    random.shuffle(candidates)
    used_names = [f["name"] for f in candidates]
    for candidate in candidates:
        if not is_faction_conflicted(candidate["name"], used_names):
            return candidate

    return random.choice(candidates)  # fallback ONLY within valid candidates


def get_compatible_place(location, race, rules):
    # Hook for future location-level filtering (e.g., sub-place restrictions)
    return random.choice(location.get("major_places", [])) if location.get("major_places") else None
