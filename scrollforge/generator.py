import json
import random
import uuid
import logging
from collections import OrderedDict
from pathlib import Path
from functools import lru_cache
from .filters import select_faction

from .filters import (
    load_rules,
    load_factions,
    filter_valid_classes,
    filter_valid_origins,
    filter_deities_by_race,
    filter_names_by_race,
    get_compatible_place,
    get_faction_relationships
)

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'

@lru_cache(maxsize=32)
def load_json(filename):
    path = DATA_DIR / filename
    if not path.exists():
        logger.error(f"Missing JSON file: {path}")
        raise FileNotFoundError(f"Required data file not found: {path}")
    try:
        with path.open('r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        logger.exception(f"Failed to load JSON from: {path}")
        return {}

def get_random_item(data, key=None):
    item = random.choice(data)
    if key and isinstance(item, dict):
        return item.get(key, "Unknown")
    return item

def sanitize_article_collisions(template, context):
    articles = ["the", "a", "an"]
    for key, value in context.items():
        if isinstance(value, str):
            for article in articles:
                article_key = f"{article} {{{key}}}"
                if article_key in template.lower():
                    lowered_value = value.lower()
                    for a in articles:
                        if lowered_value.startswith(f"{a} "):
                            context[key] = value[len(a)+1:]
                            break
    return context

def generate_backstory(context):
    backstories = load_json("backstories.json")
    class_name = context["class"]
    class_name_lower = class_name.lower()
    normalized_backstories = {k.lower(): v for k, v in backstories.items()}
    if class_name_lower not in normalized_backstories:
        return f"No backstories available for class: {class_name}"
    template = random.choice(normalized_backstories[class_name_lower])
    context = sanitize_article_collisions(template, context)
    try:
        return template.format(**context)
    except Exception as e:
        logger.warning(f"Backstory template error: {e}")
        return (
            f"A Dragon Break fractured the tale...{context.get('name', 'This soul')} "
            f"has a mysterious past, veiled in lost time."
        )

def generate_height_weight(race_name, class_name, gender_label="Unknown"):
    body_metrics = load_json("body_metrics.json")
    class_mods = load_json("class_modifiers.json")
    race_data = body_metrics.get(race_name, {})
    class_data = class_mods.get(class_name, {"height_mod": 0, "weight_mod": 0})
    gender_mods = {
        "Female": {"height_mod": -5, "weight_mod": -10},
        "Male": {"height_mod": 0, "weight_mod": 0}
    }.get(gender_label, {"height_mod": 0, "weight_mod": 0})

    if gender_label not in ["Male", "Female"]:
        logger.warning(f"Unknown gender label: {gender_label}")

    height_min, height_max = race_data.get("height", [160, 180])
    weight_min, weight_max = race_data.get("weight", [60, 80])
    height_min += class_data["height_mod"] + gender_mods["height_mod"]
    height_max += class_data["height_mod"] + gender_mods["height_mod"]
    weight_min += class_data["weight_mod"] + gender_mods["weight_mod"]
    weight_max += class_data["weight_mod"] + gender_mods["weight_mod"]

    height = random.randint(height_min, height_max)
    weight = random.randint(weight_min, weight_max)
    bmi = weight / ((height / 100) ** 2)

    if bmi > 28:
        weight = int(28 * ((height / 100) ** 2))
    elif bmi < 16:
        weight = int(16 * ((height / 100) ** 2))

    return height, weight

def find_region_by_place(locations, place_name):
    place_name_lower = place_name.lower()
    for loc in locations:
        for place in loc.get("major_places", []):
            if place.lower() == place_name_lower:
                return loc
    return None

def generate_character(overrides=None):
    try:
        rules = load_rules()
        races = load_json('races.json')
        classes = load_json('classes.json')
        locations = load_json('locations.json')
        factions = load_factions()
        celestial_marks = load_json('celestial_marks.json')
        names_data = load_json('names.json')
        fighting_styles = load_json('fighting_styles.json')
        favorite_dishes = load_json('favorite_dishes.json')
        quotes = load_json('quotes.json')
        titles = load_json('titles.json')
        genders = load_json('gender.json')
        ages_data = load_json('age.json')
        followers = load_json('follower.json')

        overrides = overrides or {}
        MAX_ATTEMPTS = 10
        force_random = overrides.get("allow_randomness") == True

        for attempt in range(MAX_ATTEMPTS):
            is_lore_compliant = not force_random and random.random() < 0.90

        # --- Normalize all override values to support case-insensitivity ---
        normalized_overrides = {k.lower(): v for k, v in overrides.items()}

        # Also ensure all string values are properly cased if expected
        def match_case_insensitive(options, target):
            if not target:
                return None
            target_lower = target.lower()
            return next((opt for opt in options if opt["name"].lower() == target_lower), None)

        def match_label_case_insensitive(options, target):
            if not target:
                return None
            target_lower = target.lower()
            return next((opt for opt in options if opt.get("label", "").lower() == target_lower), None)

        for attempt in range(MAX_ATTEMPTS):
            is_lore_compliant = not force_random and random.random() < 0.90

            race = match_case_insensitive(races, normalized_overrides.get("race")) or get_random_item(races)

            char_class_name = normalized_overrides.get("class")
            char_class = match_case_insensitive(classes, char_class_name)
            if not char_class:
                filtered_classes = filter_valid_classes(race, classes, rules) if is_lore_compliant else classes
                char_class = get_random_item(filtered_classes)

            filtered_origins = filter_valid_origins(race, locations, rules) if is_lore_compliant else locations
            filtered_followers = filter_deities_by_race(race, followers, rules) if is_lore_compliant else followers

            region_name = normalized_overrides.get("region")
            place = normalized_overrides.get("place")

            location = find_region_by_place(locations, place) if place else (
                next((loc for loc in locations if loc["name"].lower() == region_name.lower()), None)
                if region_name else get_random_item(filtered_origins)
            )

            if not place:
                place = get_compatible_place(location, race, rules) or random.choice([
                    "a remote village", "an ancient ruin", "a forgotten outpost"
                ])

            filtered_names = filter_names_by_race(race, names_data)
            name = normalized_overrides.get("name") or random.choice(filtered_names)
            gender = match_label_case_insensitive(genders, normalized_overrides.get("gender")) or get_random_item(genders)

            deity_override = normalized_overrides.get("deity")
            follower = next((f for f in followers if f["deity"].lower() == deity_override.lower()), None) if deity_override else get_random_item(filtered_followers)

            height_cm, weight_kg = generate_height_weight(race["name"], char_class["name"], gender["label"])

            faction_override = normalized_overrides.get("faction")
            faction = match_case_insensitive(factions, faction_override) or select_faction(race, char_class, factions, rules)

            age = int(normalized_overrides.get("age", -1))
            if 0 <= age:
                selected_age_group = next((a for a in ages_data if a["min"] <= age <= a["max"]), random.choice(ages_data))
            else:
                selected_age_group = random.choice(ages_data)
                age = random.randint(selected_age_group["min"], selected_age_group["max"])

            celestial_mark = match_case_insensitive(celestial_marks, normalized_overrides.get("celestial_mark")) or get_random_item(celestial_marks)
            class_fighting_styles = fighting_styles.get(char_class["name"], [])
            fighting_style = normalized_overrides.get("fighting_style") or (get_random_item(class_fighting_styles) if class_fighting_styles else "Improvised brawling")
            dish = normalized_overrides.get("favorite_dish") or get_random_item(favorite_dishes)
            class_quotes = [q["quote"] for q in quotes if q.get("class") == char_class["name"]]
            quote = normalized_overrides.get("quote") or (get_random_item(class_quotes) if class_quotes else "...")
            class_title_key = char_class["name"].capitalize()
            title_pool = titles.get(class_title_key, [])
            title = normalized_overrides.get("title") or (get_random_item(title_pool) if title_pool else "The Nameless")

            relationships = get_faction_relationships(faction["name"], factions)
            character_id = str(uuid.uuid4())

            context = {
                "id": character_id,
                "name": name,
                "title": title,
                "race": race["name"],
                "class": char_class["name"],
                "region": location["name"],
                "place": place,
                "faction": faction["name"],
                "celestial_mark": celestial_mark["name"],
                "deity": follower["deity"],
                "favorite_dish": dish,
                "fighting_style": fighting_style,
                "age": {
                    "value": age,
                    "label": selected_age_group["label"],
                    "description": selected_age_group.get("description", "")
                },
                "pronouns": gender["pronouns"]
            }

            backstory = generate_backstory(context)

            return OrderedDict([
                ("id", character_id),
                ("name", name),
                ("title", title),
                ("gender", {
                    "label": gender["label"],
                    "pronouns": gender["pronouns"]
                }),
                ("age", context["age"]),
                ("body", {
                    "height_cm": height_cm,
                    "weight_kg": weight_kg
                }),
                ("race", race),
                ("celestial_mark", celestial_mark),
                ("follower", follower),
                ("origin", {
                    "name": location["name"],
                    "place": place,
                    "description": location["description"],
                    "region_type": location.get("region_type"),
                    "environment": location.get("environment", [])
                }),
                ("class", char_class),
                ("faction", {
                    "name": faction["name"],
                    "description": faction["description"],
                    "allies": relationships["allies"],
                    "rivals": relationships["rivals"],
                    "alignment": faction.get("alignment")
                }),
                ("fighting_style", fighting_style),
                ("favorite_dish", dish),
                ("quote", quote),
                ("backstory", backstory)
            ])

        return OrderedDict([("error", "No valid character could be generated after several attempts.")])

    except Exception as e:
        logger.exception("Character generation failed.")
        return OrderedDict([
            ("error", "Something went wrong during character generation.")
        ])
