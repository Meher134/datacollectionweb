# main.py

#import argparse
import json
import os
from datetime import datetime

from .recorder import TypingRecorder
from .analyzer import TypingAnalyzer
from .spell_grammar import GrammarChecker
from .stylometry import StylometryAnalyzer
from .similarity import SimilarityChecker

def run_analysis_pipeline(raw_log_data: dict, reference_path: str, output_dir="app/uploads"):
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"typing_log_{timestamp}.json"
    log_filepath = os.path.join(output_dir, log_filename)
    
    recorder = TypingRecorder()
    recorder.run()
    log_data = recorder.get_log()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"step1_typing_log_{timestamp}.json"
    log_filepath = os.path.join(output_dir, log_filename)

    # Save raw log
    with open(log_filepath, "w") as f:
        json.dump(log_data, f, indent=2)
    print(f"\nTyping log saved to {log_filepath}")

    # Step 2: Analyze typing behavior
    analyzer = TypingAnalyzer(log_filepath)
    typing_metrics = analyzer.analyze()

    # Step 3: Grammar & spelling check
    grammar_checker = GrammarChecker(log_filepath)
    grammar_report = grammar_checker.check_grammar()

    # Step 4: Stylometry analysis
    stylometry = StylometryAnalyzer(log_filepath)
    style_report = stylometry.run()

    # Step 5: Similarity with reference
    similarity_checker = SimilarityChecker(log_filepath, reference_path)
    similarity_report = similarity_checker.compare()

    # Combine all results
    report = {
        "typing_metrics": typing_metrics,
        "grammar_report": {
            "total_issues": grammar_report["total_issues"],
            "issues": grammar_report["grammar_issues"]
        },
        "stylometry_report": style_report,
        "similarity_report": similarity_report
    }

    # Save combined report
    report_path = os.path.join(output_dir, f"analysis_report_{timestamp}.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Analysis report saved to {report_path}")

    # Print summary
    print("\n=== Summary Report ===")
    print(f"Typing Metrics:\n{typing_metrics}")
    print(f"\nGrammar Issues: {grammar_report['total_issues']}")
    print(f"Stylometry Drift Score: {style_report.get('drift_score', 'N/A'):.3f}")
    print(f"Similarity Score: {similarity_report['similarity_score']:.3f} ({similarity_report['interpretation']})")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Typing Behavior Analysis Pipeline")
    parser.add_argument("reference", help="Path to reference text file")
    parser.add_argument("--output_dir", default="outputs", help="Directory to save logs and reports")

    args = parser.parse_args()
    run_pipeline(args.reference, args.output_dir)
