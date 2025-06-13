import os
from flask import Flask
from pymongo import MongoClient
from dotenv import load_dotenv

def create_app():
    app = Flask(__name__)

    # Load environment variables from .env (only needed locally)
    load_dotenv()

    # Connect to MongoDB Atlas using MONGO_URI from .env or deployment environment
    mongo_uri = os.environ.get("MONGO_URI")
    client = MongoClient(mongo_uri)

    # Select your database
    db = client["typing_db"]

    # Store database in app config so you can access it elsewhere (e.g., in routes)
    app.config["MONGO_DB"] = db

    # Register your blueprint
    from app.routes import main
    app.register_blueprint(main)

    return app
