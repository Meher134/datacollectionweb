# spell_grammar.py

import json
import language_tool_python

class GrammarChecker:
    def __init__(self, filepath):
        with open(filepath, "r") as f:
            self.data = json.load(f)

        self.words = self.data.get("words", [])
        self.full_text = self._reconstruct_text()

        self.tool = language_tool_python.LanguageTool('en-US')

    def _reconstruct_text(self):
        # Join words and split by spacing/enter manually
        reconstructed = " ".join([w["word"] for w in self.words])
        return reconstructed.strip()

    def check_grammar(self):
        matches = self.tool.check(self.full_text)

        grammar_issues = []
        for match in matches:
            grammar_issues.append({
                "message": match.message,
                "rule": match.ruleId,
                "category": match.ruleIssueType,
                "incorrect_text": match.context[match.offset: match.offset + match.errorLength],
                "suggestions": match.replacements,
                "offset": match.offset
            })

        return {
            "text": self.full_text,
            "grammar_issues": grammar_issues,
            "total_issues": len(grammar_issues)
        }

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("input_json", help="Path to the JSON output from recorder.py")
    args = parser.parse_args()

    checker = GrammarChecker(args.input_json)
    result = checker.check_grammar()

    print("\n=== Essay Text ===")
    print(result["text"])
    print("\n=== Grammar & Spelling Issues ===")
    for issue in result["grammar_issues"]:
        print(f"- {issue['incorrect_text']} → {issue['suggestions']} ({issue['message']})")
    print(f"\nTotal Issues: {result['total_issues']}")
