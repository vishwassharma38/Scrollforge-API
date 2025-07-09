from flask import Blueprint, request, Response
import logging
import json
from .generator import generate_character

logger = logging.getLogger(__name__)

main = Blueprint('main', __name__)

@main.route('/generate', methods=['GET'])
def generate():
    try:
        character = generate_character()
        return Response(
        json.dumps(character, indent=2, ensure_ascii=False),
        mimetype="application/json"
    )
    except Exception as e:
        logger.exception("Uncaught error during /generate")
        return Response(
            json.dumps({"error": "Internal server error"}, indent=2, ensure_ascii=False),
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
        json.dumps(character, indent=2, ensure_ascii=False),
        mimetype="application/json"
    )
    except Exception as e:
        logger.exception("Custom generation failed at /custom_generate")
        return Response(
            json.dumps({
                "error": "Custom character generation failed",
                "details": str(e)
            }, indent=2, ensure_ascii=False),
            mimetype="application/json",
            status=500
        )

@main.route('/', methods=['GET'])
def welcome():
    return Response(
        json.dumps({
            "message": "Welcome to Scrollforge API — use /generate or /custom_generate to summon a character."
        }, indent=2, ensure_ascii=False),
        mimetype="application/json"
    )
