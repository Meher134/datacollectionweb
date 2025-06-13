# stylometry.py

import json
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk import pos_tag
from sentence_transformers import SentenceTransformer, util
from statistics import mean

class StylometryAnalyzer:
    def __init__(self, filepath):
        with open(filepath, "r") as f:
            self.data = json.load(f)
        self.text = self._reconstruct_text()
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight for drift

    def _reconstruct_text(self):
        return " ".join([w["word"] for w in self.data.get("words", [])])

    def basic_stylometry(self):
        words = word_tokenize(self.text)
        sentences = sent_tokenize(self.text)

        punctuations = [w for w in words if w in ".,!?;:"]
        avg_sentence_len = mean([len(word_tokenize(s)) for s in sentences]) if sentences else 0
        avg_word_len = mean([len(w) for w in words if w.isalpha()]) if words else 0
        lexical_diversity = len(set(words)) / len(words) if words else 0

        return {
            "total_sentences": len(sentences),
            "total_words": len(words),
            "avg_sentence_length": avg_sentence_len,
            "avg_word_length": avg_word_len,
            "punctuation_count": len(punctuations),
            "lexical_diversity": lexical_diversity
        }

    def drift_analysis(self):
        sentences = sent_tokenize(self.text)
        if len(sentences) < 4:
            return {"drift_score": 0, "note": "Too few sentences to detect drift."}

        chunks = [ " ".join(sentences[i:i+2]) for i in range(0, len(sentences), 2) ]
        embeddings = self.model.encode(chunks, convert_to_tensor=True)
        similarities = [float(util.cos_sim(embeddings[i], embeddings[i+1])) for i in range(len(embeddings)-1)]

        drift_score = 1 - mean(similarities)  # Higher = more drift
        return {
            "drift_score": drift_score,
            "semantic_similarities": similarities,
            "interpretation": "High drift may indicate copying if style suddenly changes."
        }

    def run(self):
        style = self.basic_stylometry()
        drift = self.drift_analysis()
        return {**style, **drift}

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("input_json", help="Path to the JSON output from recorder.py")
    args = parser.parse_args()

    analyzer = StylometryAnalyzer(args.input_json)
    results = analyzer.run()

    print("\n=== Stylometric & Semantic Analysis ===")
    for k, v in results.items():
        print(f"{k}: {v}")
