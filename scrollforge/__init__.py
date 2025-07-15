from flask import Flask
from flask_cors import CORS  # 🧪 New import!

def create_app():
    app = Flask(__name__)
    
    # 🌐 Enable CORS for all routes and origins (restrict later if needed)
    CORS(app)

    from .routes import main
    app.register_blueprint(main)

    return app
