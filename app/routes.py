import os
import json
from datetime import datetime
from flask import Blueprint, request, render_template, jsonify
from flask import current_app

from app.utils.analyzer import TypingAnalyzer
from app.utils.spell_grammar import GrammarChecker
from app.utils.stylometry import StylometryAnalyzer


main = Blueprint('main', __name__)

UPLOAD_DIR = os.path.join("app", "uploads")
REFERENCE_PATH = os.path.join("app", "utils", "reference.txt")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@main.route("/")
def home():
    return render_template("typing.html")  # Typing interface


@main.route("/submit", methods=["POST"])
def submit_typing_data():
    try:
        data = request.get_json()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"typing_log_{timestamp}.json"
        log_filepath = os.path.join(UPLOAD_DIR, log_filename)

        # Save raw typing session
        with open(log_filepath, "w") as f:
            json.dump(data, f, indent=2)

        # Step 1: Typing Behavior Metrics
        analyzer = TypingAnalyzer(log_filepath)
        typing_metrics = analyzer.analyze()

        # Step 2: Grammar & Spelling
        grammar_checker = GrammarChecker(log_filepath)
        grammar_report = grammar_checker.check_grammar()

        # Step 3: Stylometry
        stylometry = StylometryAnalyzer(log_filepath)
        style_report = stylometry.run()

        

        # Full Report
        report = {
            "typing_metrics": typing_metrics,
            "grammar_report": {
                "total_issues": grammar_report["total_issues"],
                "issues": grammar_report["grammar_issues"]
            },
            "stylometry_report": style_report,
            
        }
        # Save the full report
        # Append report to original typing data
        data["report"] = report
        with open(log_filepath, "w") as f:
            json.dump(data, f, indent=2)
        
        # Access the MongoDB collection
        db = current_app.config['MONGO_DB']
        reports_collection = db["reports"]

        # Store report in MongoDB
        reports_collection.insert_one({
            "timestamp": timestamp,
            "raw_data": data,
            "report": report
        })

        return jsonify({
            "status": "success",
            "message": "Analysis completed.",
            "report": report
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "An error occurred during analysis.",
            "error": str(e)
        }), 500
