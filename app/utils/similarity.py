# similarity.py

import json
from sentence_transformers import SentenceTransformer, util

class SimilarityChecker:
    def __init__(self, typed_json_path, reference_txt_path):
        self.typed_text = self._load_typed_text(typed_json_path)
        self.reference_text = self._load_reference_text(reference_txt_path)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def _load_typed_text(self, path):
        with open(path, "r") as f:
            data = json.load(f)
        return " ".join([w["word"] for w in data.get("words", [])])

    def _load_reference_text(self, path):
        with open(path, "r") as f:
            return f.read()

    def compare(self):
        typed_emb = self.model.encode(self.typed_text, convert_to_tensor=True)
        ref_emb = self.model.encode(self.reference_text, convert_to_tensor=True)

        similarity_score = float(util.cos_sim(typed_emb, ref_emb))
        interpretation = (
            "Very High" if similarity_score > 0.90 else
            "High" if similarity_score > 0.75 else
            "Moderate" if similarity_score > 0.50 else
            "Low"
        )

        return {
            "similarity_score": similarity_score,
            "interpretation": interpretation
        }

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("typed_json", help="Path to recorded JSON file")
    parser.add_argument("reference_txt", help="Path to reference text file")
    args = parser.parse_args()

    checker = SimilarityChecker(args.typed_json, args.reference_txt)
    result = checker.compare()

    print("\n=== Similarity with Reference ===")
    print(f"Score: {result['similarity_score']:.4f}")
    print(f"Interpretation: {result['interpretation']}")
