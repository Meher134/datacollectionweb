# dataset_builder.py

import os
import json
import glob
import pandas as pd
from analyzer import TypingAnalyzer
from spell_grammar import GrammarChecker
from stylometry import StylometryAnalyzer
from similarity import SimilarityChecker

class DatasetBuilder:
    def __init__(self, logs_dir, reference_file):
        self.logs_dir = logs_dir
        self.reference_file = reference_file
        self.dataset = []

    def build(self):
        log_files = glob.glob(os.path.join(self.logs_dir, "step1_typing_log_*.json"))

        for log_path in log_files:
            print(f"Processing: {log_path}")
            entry = {"file": os.path.basename(log_path)}

            try:
                # Typing behavior
                analyzer = TypingAnalyzer(log_path)
                entry.update(analyzer.analyze())

                # Grammar & spelling
                grammar = GrammarChecker(log_path)
                grammar_data = grammar.check_grammar()
                entry["grammar_issue_count"] = grammar_data["total_issues"]

                # Stylometry
                style = StylometryAnalyzer(log_path)
                entry.update(style.run())

                # Similarity
                sim = SimilarityChecker(log_path, self.reference_file)
                sim_result = sim.compare()
                entry["similarity_score"] = sim_result["similarity_score"]
                entry["similarity_interpretation"] = sim_result["interpretation"]

                self.dataset.append(entry)

            except Exception as e:
                print(f"Error processing {log_path}: {e}")
                continue

        return self.dataset

    def save(self, output_path="typing_dataset.csv"):
        df = pd.DataFrame(self.dataset)
        df.to_csv(output_path, index=False)
        print(f"Dataset saved to {output_path}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--logs_dir", default=".", help="Directory with typing log JSONs")
    parser.add_argument("--reference", required=True, help="Reference .txt file path")
    parser.add_argument("--output", default="typing_dataset.csv", help="Output CSV file")

    args = parser.parse_args()

    builder = DatasetBuilder(args.logs_dir, args.reference)
    builder.build()
    builder.save(args.output)
