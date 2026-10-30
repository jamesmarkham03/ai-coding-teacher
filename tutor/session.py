"""One study session: teach a concept, check it with a quick question, then a coding question.

Run with: python -m tutor.session [--language python] [--concept lists]
"""
import argparse
import importlib.util
import random
from pathlib import Path

from tutor.bank import concepts_for, load_bank, questions_for
from tutor.scoring import language_score, load_scores, record_result, save_scores, weakest_concept

ROOT = Path(__file__).resolve().parent.parent
BANK_PATH = ROOT / "data" / "question_bank.json"
SCORES_PATH = ROOT / "data" / "scores.json"
LESSONS_DIR = ROOT / "data" / "lessons"
SOLUTIONS_DIR = ROOT / "solutions"


def show_lesson(language, concept):
    lesson = LESSONS_DIR / language / f"{concept}.md"
    print(lesson.read_text(encoding="utf-8"))


def normalize(text):
    """Make quick-answer checking forgiving about case and spaces."""
    return text.strip().lower().replace(" ", "")


def run_quick(question):
    """Ask a short question and return True if the answer matches."""
    print(f"\nQuick check: {question['prompt']}")
    reply = input("Your answer: ")
    correct = normalize(reply) == normalize(str(question["answer"]))
    print("Correct!" if correct else f"Not quite. The answer is {question['answer']}.")
    return correct


def load_solution(path, function_name):
    """Import the solution file fresh, so edits are picked up on every run."""
    spec = importlib.util.spec_from_file_location("solution", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, function_name)


def run_tests(question, path):
    """Run every test case and print the ones that fail. Return True if all pass."""
    try:
        function = load_solution(path, question["function"])
    except Exception as error:  # show the student their own error, not a crash
        print(f"Could not load your solution: {error}")
        return False

    all_passed = True
    for test in question["tests"]:
        try:
            got = function(*test["args"])
        except Exception as error:
            print(f"  args {test['args']}: raised {type(error).__name__}: {error}")
            all_passed = False
            continue
        if got != test["expected"]:
            print(f"  args {test['args']}: expected {test['expected']!r}, got {got!r}")
            all_passed = False
    return all_passed


def run_coding(question):
    """Give a coding question, let the student write it, and test their code."""
    path = SOLUTIONS_DIR / f"{question['id']}.py"
    SOLUTIONS_DIR.mkdir(exist_ok=True)
    if not path.exists():
        path.write_text(f"# {question['prompt']}\n\ndef {question['function']}(*args):\n    pass\n",
                        encoding="utf-8")

    print(f"\nCoding question: {question['prompt']}")
    print(f"Write your answer in: {path}")
    while True:
        reply = input("Save the file and press Enter to test it (or type 'skip'): ")
        if reply.strip().lower() == "skip":
            print("Skipped. This counts as a miss.")
            return False
        if run_tests(question, path):
            print("All tests passed!")
            return True
        print("Some tests failed. Fix the file and try again.")


def run_session(language, concept, bank, scores):
    """Teach, check and test one concept, then save the results."""
    print(f"\n=== {language.title()}: {concept} ===\n")
    show_lesson(language, concept)

    results = []
    quick = random.choice(questions_for(bank, language, concept, "quick"))
    results.append(run_quick(quick))

    coding = random.choice(questions_for(bank, language, concept, "coding"))
    results.append(run_coding(coding))

    for correct in results:
        record_result(scores, language, concept, correct)
    save_scores(scores, SCORES_PATH)

    print(f"\nSession result: {sum(results)}/{len(results)} correct.")
    print(f"{concept} score is now {scores[language][concept]['score']}.")
    print(f"{language.title()} average: {language_score(scores, language)}.")


def main():
    parser = argparse.ArgumentParser(description="Run one coding study session.")
    parser.add_argument("--language", default="python")
    parser.add_argument("--concept", help="Study this concept. Default: your weakest one.")
    args = parser.parse_args()

    bank = load_bank(BANK_PATH)
    scores = load_scores(SCORES_PATH)
    concepts = concepts_for(bank, args.language)
    if not concepts:
        raise SystemExit(f"No questions for language {args.language!r} yet.")

    concept = args.concept or weakest_concept(scores, args.language, concepts)
    if concept not in concepts:
        raise SystemExit(f"Unknown concept {concept!r}. Choose from: {', '.join(concepts)}")

    run_session(args.language, concept, bank, scores)


if __name__ == "__main__":
    main()
