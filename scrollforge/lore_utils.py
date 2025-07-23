import logging
from pathlib import Path
from collections import OrderedDict
from functools import lru_cache
import json

logger = logging.getLogger(__name__)
LORE_DIR = Path(__file__).resolve().parent / 'data'

@lru_cache(maxsize=8)
def load_lore_file(lore_type):
    """
    Load the appropriate lore file from disk based on the type (race, class, faction, location).
    """
    mapping = {
        "race": "lore_races.json",
        "class": "lore_classes.json",
        "faction": "lore_factions.json",
        "location": "lore_locations.json"
    }
    filename = mapping.get(lore_type.lower())
    if not filename:
        logger.warning(f"No file mapping for lore type '{lore_type}'")
        return {}

    path = LORE_DIR / filename
    if not path.exists():
        logger.warning(f"Lore file not found: {path}")
        return {}

    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        logger.exception(f"Failed to load lore file '{filename}': {e}")
        return {}

def format_race_lore_entry(name, entry):
    """
    Format and order a race lore entry for consistent API output.
    """
    appearance = entry.get("appearance", {})
    beliefs = entry.get("beliefs", {})
    government = entry.get("government", {})
    council = government.get("council_details", {})
    magic = entry.get("magic", {})
    magic_lang = magic.get("language", {})
    architecture = entry.get("architecture", {})
    conflicts = entry.get("internal_conflicts", {})
    diplomacy = entry.get("diplomacy", {})

    # Normalize forbidden content from multiple key names
    forbidden = (
        conflicts.get("forbidden") or
        conflicts.get("forbidden_relics") or
        conflicts.get("forbidden_rites") or
        conflicts.get("forbidden_knowledge")
    )

    internal_conflicts = OrderedDict()
    if "emerging_factions" in conflicts:
        internal_conflicts["emerging_factions"] = conflicts["emerging_factions"]
    if forbidden:
        internal_conflicts["forbidden"] = forbidden

    ordered_lore = OrderedDict([
        ("origin", entry.get("origin", "")),
        ("summary", entry.get("summary", "")),
        ("native_land", entry.get("native_land", "")),
        ("physiology", entry.get("physiology", "")),

        ("appearance", OrderedDict([
            ("skin", appearance.get("skin", "")),
            ("eyes", appearance.get("eyes", "")),
            ("hair", appearance.get("hair", ""))
        ])),

        ("culture", entry.get("culture", "")),
        ("customs", entry.get("customs", [])),

        ("beliefs", OrderedDict([
            ("primary_doctrine", beliefs.get("primary_doctrine", "")),
            ("afterlife", beliefs.get("afterlife", "")),
            ("view_on_divinity", beliefs.get("view_on_divinity", "")),
            ("gods", beliefs.get("gods", ""))
        ])),

        ("government", OrderedDict([
            ("structure", government.get("structure", "")),
            ("ruling_body", government.get("ruling_body", "")),
            ("council_details", OrderedDict([
                ("number_of_members", council.get("number_of_members", "")),
                ("trial_required", council.get("trial_required", "")),
                ("philosophical_veils", council.get("philosophical_veils", []))
            ])),
            ("political_view", government.get("political_view", ""))
        ])),

        ("magic", OrderedDict([
            ("affinity", magic.get("affinity", [])),
            ("prodigy_rate", magic.get("prodigy_rate", "")),
            ("elite_spellcasters", magic.get("elite_spellcasters", "")),
            ("language", OrderedDict([
                ("name", magic_lang.get("name", "")),
                ("properties", magic_lang.get("properties", ""))
            ]))
        ])),

        ("architecture", OrderedDict([
            ("style", architecture.get("style", "")),
            ("location", architecture.get("location", ""))
        ])),

        ("factions", entry.get("factions", [])),
        ("internal_conflicts", internal_conflicts),

        ("diplomacy", OrderedDict([
            ("view_of_other_races", diplomacy.get("view_of_other_races", {})),
            ("diplomatic_methods", diplomacy.get("diplomatic_methods", ""))
        ]))
    ])

    return OrderedDict([
        ("name", name),
        ("type", "race"),
        ("lore", ordered_lore)
    ])


def format_class_lore_entry(name, entry):
    """
    Format and order a class lore entry for elegant output.
    """
    ordered_lore = OrderedDict([
        ("description", entry.get("description", "")),
        ("story", entry.get("story", "")),
        ("alignment", entry.get("alignment", "")),
        ("merits", entry.get("merits", [])),
        ("demerits", entry.get("demerits", []))
    ])

    return OrderedDict([
        ("name", name),
        ("type", "class"),
        ("lore", ordered_lore)
    ])


def format_faction_lore_entry(name, entry):
    """
    Format and order a faction lore entry for clean output.
    """
    structure = entry.get("structure", {})
    symbols = entry.get("symbols", {})

    ordered_lore = OrderedDict([
        ("description", entry.get("description", "")),
        ("story", entry.get("story", "")),
        ("alignment", entry.get("alignment", "")),
        ("allies", entry.get("allies", [])),
        ("rivals", entry.get("rivals", [])),

        ("structure", OrderedDict([
            ("guildmaster_title", structure.get("guildmaster_title", "")),
            ("roles", structure.get("roles", []))
        ])),

        ("notable_events", entry.get("notable_events", [])),
        ("relationships", entry.get("relationships", {})),

        ("symbols", OrderedDict([
            ("guild_mark", symbols.get("guild_mark", "")),
            ("hand_signals", symbols.get("hand_signals", {}))
        ]))
    ])

    return OrderedDict([
        ("name", name),
        ("type", "faction"),
        ("lore", ordered_lore)
    ])
