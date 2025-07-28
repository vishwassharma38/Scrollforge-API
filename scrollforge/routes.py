from flask import Blueprint, request, Response, jsonify
import logging
import json
import random
from collections import OrderedDict
from .generator import generate_character
from .lore_utils import (
    load_lore_file,
    format_race_lore_entry,
    format_faction_lore_entry,
    format_class_lore_entry,
    load_location_lore,
    format_location_lore_entry
)

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
    try:
        lore_type = random.choice(['race', 'class', 'faction', 'location'])

        if lore_type == "race":
            data = load_lore_file("race")
            name = random.choice(list(data.keys()))
            entry = data[name]
            formatted = format_race_lore_entry(name, entry)

        elif lore_type == "class":
            data = load_lore_file("class")
            entry = random.choice(data)
            name = entry.get("name", "Unknown Class")
            formatted = format_class_lore_entry(name, entry)

        elif lore_type == "faction":
            data = load_lore_file("faction")
            entry = random.choice(data)
            name = entry.get("name", "Unknown Faction")
            formatted = format_faction_lore_entry(name, entry)

        elif lore_type == "location":
            data = load_location_lore()
            entry = random.choice(data)
            formatted = format_location_lore_entry(entry)

        return Response(
            json.dumps({lore_type: formatted}, indent=2, ensure_ascii=False, sort_keys=False),
            mimetype="application/json"
        )

    except Exception as e:
        logger.exception("Uncaught error during /lore")
        return Response(
            json.dumps({"error": "Internal server error"}, indent=2),
            mimetype="application/json",
            status=500
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


@main.route('/lore/location', methods=['GET'])
@main.route('/location', methods=['GET'])
def get_random_location():
    data = load_location_lore()
    if not data:
        return jsonify({"error": "No location lore data found."}), 404
    selected = random.choice(data)
    formatted = format_location_lore_entry(selected)
    return Response(
        json.dumps(formatted, indent=2, ensure_ascii=False, sort_keys=False),
        mimetype="application/json"
    )


@main.route('/lore/location/<string:location_name>', methods=['GET'])
def get_location_by_name(location_name):
    try:
        data = load_location_lore()
        for loc in data:
            if loc["name"].lower().replace(" ", "") == location_name.lower().replace(" ", ""):
                formatted = format_location_lore_entry(loc)
                return Response(
                    json.dumps(formatted, indent=2, ensure_ascii=False, sort_keys=False),
                    mimetype="application/json"
                )
        return jsonify({"error": f"Location '{location_name}' not found."}), 404
    except Exception as e:
        logger.error(f"Error fetching location '{location_name}': {str(e)}")
        return jsonify({"error": "Failed to load location data."}), 500



@main.route('/generate/bulk', methods=['GET'])
def generate_bulk_from_query():
    try:
        args = request.args.to_dict()
        count_str = args.pop("count", "4")

        # Safely convert count
        try:
            count = int(count_str)
            if count < 1 or count > 100:
                raise ValueError
        except ValueError:
            return jsonify({"error": "Count must be an integer between 1 and 100"}), 400

        # Parse comma-separated values and normalize keys/values to lowercase
        parsed_overrides = {}
        for key, value in args.items():
            norm_key = key.lower()  # Normalize the parameter name
            values = [v.strip().lower() for v in value.split(",")]  # Normalize values
            parsed_overrides[norm_key] = values

        generated = []

        for i in range(count):
            overrides = {}
            for key, values in parsed_overrides.items():
                if i < len(values):
                    val = values[i]
                else:
                    val = random.choice(values)

                # Convert age if applicable
                if key == "age":
                    try:
                        overrides[key] = int(val)
                    except ValueError:
                        continue
                else:
                    overrides[key] = val

            character = generate_character(overrides)
            generated.append(character)

        response_data = OrderedDict([
            ("count", count),
            ("overrides_pool", parsed_overrides),
            ("generated", generated)
        ])

        return Response(
            json.dumps(response_data, indent=2),
            mimetype='application/json'
        )

    except Exception as e:
        logger.exception("Advanced bulk generation failed.")
        return jsonify({"error": "Something went wrong"}), 500

    except Exception as e:
        logger.exception("Advanced bulk generation failed.")
        return jsonify({"error": "Something went wrong"}), 500


@main.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "I'm Alive!", "version": "v1"})