"""Print your score for every concept, grouped by language, with the language average.

Run with: python -m tutor.show_scores
"""
from tutor.scoring import language_score, load_scores
from tutor.session import SCORES_PATH


def format_report(scores):
    """Build the report as text so it is easy to test."""
    if not scores:
        return "No sessions yet. Run: python -m tutor.session"

    lines = []
    for language in scores:
        lines.append(f"{language.title()} (average {language_score(scores, language)})")
        lines.append(f"  {'concept':<16}{'score':>8}{'attempts':>10}")
        for concept, entry in sorted(scores[language].items(), key=lambda item: item[1]["score"]):
            lines.append(f"  {concept:<16}{entry['score']:>8}{entry['attempts']:>10}")
        lines.append("")
    return "\n".join(lines).rstrip()


def main():
    print(format_report(load_scores(SCORES_PATH)))


if __name__ == "__main__":
    main()
