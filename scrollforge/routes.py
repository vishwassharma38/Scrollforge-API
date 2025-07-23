from flask import Blueprint, request, Response, jsonify
import logging
import json
import random
from .generator import generate_character
from .lore_utils import load_lore_file, format_race_lore_entry, format_faction_lore_entry, format_class_lore_entry

logger = logging.getLogger(__name__)
main = Blueprint('main', __name__)


@main.route('/', methods=['GET'])
def welcome():
    return Response(
        json.dumps({
            "message": "Welcome to Scrollforge API — use /generate or /custom_generate to summon a character."
        }, indent=2, ensure_ascii=False, sort_keys=False),
        mimetype="application/json"
    )


@main.route('/generate', methods=['GET'])
def generate():
    try:
        character = generate_character()
        return Response(
            json.dumps(character, indent=2, ensure_ascii=False, sort_keys=False),
            mimetype="application/json"
        )
    except Exception as e:
        logger.exception("Uncaught error during /generate")
        return Response(
            json.dumps({"error": "Internal server error"}, indent=2, ensure_ascii=False, sort_keys=False),
            mimetype="application/json",
            status=500
        )


@main.route('/custom_generate', methods=['GET'])
def custom_generate():
    try:
        raw_params = {k.lower(): v for k, v in request.args.items()}
        overrides = {
            k: v.title() if k in ["race", "class", "faction", "gender"] else v
            for k, v in raw_params.items()
        }
        character = generate_character(overrides=overrides)
        return Response(
            json.dumps(character, indent=2, ensure_ascii=False, sort_keys=False),
            mimetype="application/json"
        )
    except Exception as e:
        logger.exception("Custom generation failed at /custom_generate")
        return Response(
            json.dumps({
                "error": "Custom character generation failed",
                "details": str(e)
            }, indent=2, ensure_ascii=False, sort_keys=False),
            mimetype="application/json",
            status=500
        )


@main.route('/lore', methods=['GET'])
def random_lore():
    lore_types = ["race", "faction", "class",]
    chosen_type = random.choice(lore_types)
    lore_data = load_lore_file(chosen_type)

    if not lore_data:
        return Response(
            json.dumps({"error": "Lore data not found."}, indent=2),
            mimetype="application/json",
            status=404
        )

    if chosen_type == "race":
        name = random.choice(list(lore_data.keys()))
        entry = lore_data[name]
        formatted = format_race_lore_entry(name, entry)
    elif chosen_type == "class":
        name = random.choice(list(lore_data.keys()))
        entry = lore_data[name]
        formatted = format_class_lore_entry(name, entry)
    else:
        entry = random.choice(lore_data)
        name = entry.get("name", "Unknown Faction")
        formatted = format_faction_lore_entry(name, entry)

    return Response(
        json.dumps(formatted, indent=2, ensure_ascii=False, sort_keys=False),
        mimetype="application/json"
    )


@main.route('/lore/race', methods=['GET'])
@main.route('/race', methods=['GET'])
def random_race():
    lore_data = load_lore_file("race")
    if not lore_data or not isinstance(lore_data, dict):
        return Response(
            json.dumps({"error": "Race data not available."}, indent=2),
            status=404,
            mimetype="application/json"
        )

    name = random.choice(list(lore_data.keys()))
    entry = lore_data[name]
    formatted = format_race_lore_entry(name, entry)

    return Response(
        json.dumps(formatted, indent=2, ensure_ascii=False, sort_keys=False),
        mimetype="application/json"
    )


@main.route('/lore/race/<name>', methods=['GET'])
@main.route('/race/<name>', methods=['GET'])
def lore_race(name):
    lore_data = load_lore_file("race")
    entry = next((v for k, v in lore_data.items() if k.lower() == name.lower()), None)
    proper_name = next((k for k in lore_data if k.lower() == name.lower()), name)

    if not entry:
        return Response(
            json.dumps({"error": f"No race found named '{name}'"}, indent=2),
            status=404,
            mimetype="application/json"
        )

    formatted_lore = format_race_lore_entry(proper_name, entry)
    return Response(
        json.dumps(formatted_lore, indent=2, ensure_ascii=False, sort_keys=False),
        mimetype="application/json"
    )

@main.route('/lore/class', methods=['GET'])
@main.route('/class', methods=['GET'])
def random_class():
    lore_data = load_lore_file("class")
    if not lore_data or not isinstance(lore_data, list):
        return Response(
            json.dumps({"error": "No class lore available."}, indent=2),
            status=404,
            mimetype="application/json"
        )

    entry = random.choice(lore_data)
    name = entry.get("name", "Unknown Class")
    formatted = format_class_lore_entry(name, entry)

    return Response(
        json.dumps(formatted, indent=2, ensure_ascii=False, sort_keys=False),
        mimetype="application/json"
    )

@main.route('/lore/class/<name>', methods=['GET'])
@main.route('/class/<name>', methods=['GET'])
def lore_class(name):
    lore_data = load_lore_file("class")

    entry = next((c for c in lore_data if c.get("name", "").lower() == name.lower()), None)
    proper_name = entry["name"] if entry else name

    if not entry:
        return Response(
            json.dumps({"error": f"No class found named '{name}'"}, indent=2),
            status=404,
            mimetype="application/json"
        )

    formatted = format_class_lore_entry(proper_name, entry)

    return Response(
        json.dumps(formatted, indent=2, ensure_ascii=False, sort_keys=False),
        mimetype="application/json"
    )

@main.route('/lore/faction', methods=['GET'])
@main.route('/faction', methods=['GET'])
def random_faction():
    lore_data = load_lore_file("faction")

    if not lore_data or not isinstance(lore_data, list):
        return Response(
            json.dumps({"error": "No faction data available."}, indent=2),
            status=404,
            mimetype="application/json"
        )

    entry = random.choice(lore_data)
    name = entry.get("name", "Unknown Faction")
    formatted = format_faction_lore_entry(name, entry)

    return Response(
        json.dumps(formatted, indent=2, ensure_ascii=False, sort_keys=False),
        mimetype="application/json"
    )

@main.route('/lore/faction/<name>', methods=['GET'])
@main.route('/faction/<name>', methods=['GET'])
def lore_faction(name):
    lore_data = load_lore_file("faction")

    entry = next((f for f in lore_data if f.get("name", "").lower() == name.lower()), None)
    proper_name = entry["name"] if entry else name

    if not entry:
        return Response(
            json.dumps({"error": f"No faction found named '{name}'"}, indent=2),
            status=404,
            mimetype="application/json"
        )

    formatted = format_faction_lore_entry(proper_name, entry)

    return Response(
        json.dumps(formatted, indent=2, ensure_ascii=False, sort_keys=False),
        mimetype="application/json"
    )


@main.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "ok", "version": "v1"})
