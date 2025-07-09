import json
import random
import uuid
import logging
from collections import OrderedDict
from pathlib import Path
from functools import lru_cache

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

@lru_cache(maxsize=32)
def load_json(filename):
    path = BASE_DIR / 'data' / filename
    with path.open('r', encoding='utf-8') as file:
        return json.load(file)

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

def is_faction_conflicted(faction_name, selected_factions):
    factions_data = load_factions()
    faction = next((f for f in factions_data if f["name"] == faction_name), None)
    if not faction:
        return False
    rivals = set(faction.get("rivals", []))
    for other in factions_data:
        if faction_name in other.get("rivals", []):
            rivals.add(other["name"])
    return any(r in selected_factions for r in rivals)

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
        celestial_marks = load_json('Celestial_marks.json')
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

        for attempt in range(MAX_ATTEMPTS):
            race = next((r for r in races if r["name"] == overrides.get("race")), None) or get_random_item(races)
            filtered_classes = filter_valid_classes(race, classes, rules)
            char_class = next((c for c in filtered_classes if c["name"] == overrides.get("class")), None)
            if not char_class and overrides.get("class"):
                char_class = next((c for c in classes if c["name"] == overrides["class"]), get_random_item(classes))
            elif not char_class and filtered_classes:
                char_class = get_random_item(filtered_classes)

            if not char_class:
                continue

            place = overrides.get("place")
            location = find_region_by_place(locations, place) if place else None

            if not location:
                filtered_locations = filter_valid_origins(race, locations, rules)
                location = next((loc for loc in filtered_locations if loc["name"] == overrides.get("region")), None)
                if not location:
                    location = get_random_item(filtered_locations if filtered_locations else locations)
                place = get_compatible_place(location, race, rules) or random.choice(["a remote village", "an ancient ruin", "a forgotten outpost"])

            filtered_names = filter_names_by_race(race, names_data)
            name = overrides.get("name") or random.choice(filtered_names)
            gender = next((g for g in genders if g["label"] == overrides.get("gender")), None) or get_random_item(genders)

            class_allowed_factions = rules["class_faction_allowed"].get(char_class["name"], [])
            race_invalid_factions = rules["invalid_race_faction"].get(race["name"], [])
            preferred_factions = [f for f in factions if f["name"] in class_allowed_factions and f["name"] not in race_invalid_factions]
            fallback_factions = [f for f in factions if f["name"] in class_allowed_factions]
            valid_faction_candidates = preferred_factions if preferred_factions else fallback_factions

            faction = next((f for f in factions if f["name"] == overrides.get("faction")), None)
            if not faction:
                random.shuffle(valid_faction_candidates)
                faction = next((f for f in valid_faction_candidates if not is_faction_conflicted(f["name"], [x["name"] for x in valid_faction_candidates])), None)
                if not faction:
                    faction = get_random_item(factions)

            filtered_followers = filter_deities_by_race(race, followers, rules)
            follower = next((f for f in filtered_followers if f["deity"] == overrides.get("deity")), None) if overrides.get("deity") else (get_random_item(filtered_followers) if filtered_followers else get_random_item(followers))

            height_cm, weight_kg = generate_height_weight(race["name"], char_class["name"], gender["label"])

            selected_age_group = next((a for a in ages_data if a["label"] == overrides.get("age_label")), None)
            if not selected_age_group:
                young_groups = [a for a in ages_data if a["max"] < 50]
                elder_groups = [a for a in ages_data if a["max"] >= 50]
                selected_age_group = random.choice(young_groups if random.random() < 0.85 else elder_groups)
            age = int(overrides.get("age", random.randint(selected_age_group["min"], selected_age_group["max"])))

            celestial_mark = next((cm for cm in celestial_marks if cm["name"] == overrides.get("celestial_mark")), None) or get_random_item(celestial_marks)
            class_fighting_styles = fighting_styles.get(char_class["name"], [])
            fighting_style = overrides.get("fighting_style") or (get_random_item(class_fighting_styles) if class_fighting_styles else "Improvised brawling")
            dish = overrides.get("favorite_dish") or get_random_item(favorite_dishes)
            class_quotes = [q["quote"] for q in quotes if q.get("class") == char_class["name"]]
            quote = overrides.get("quote") or (get_random_item(class_quotes) if class_quotes else "...")
            class_title_key = char_class["name"].capitalize()
            title_pool = titles.get(class_title_key, [])
            title = overrides.get("title") or (get_random_item(title_pool) if title_pool else "The Nameless")

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
