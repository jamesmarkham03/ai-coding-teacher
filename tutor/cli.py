"""Command line entry point:  python -m tutor <command>

Studying is done by the /learn skill in Claude Code, which uses these helpers:
next        which concept to study next, its lesson file and the questions to ask
question    show one question (never its answer)
check       test an answer or a solution file for one question
record      log a result so scores update

scores     per-concept and per-language scores, due reviews, what to do next
checklist   general interview topics: covered vs missed
prep        build a study plan from a job description or company
mock        timed mock coding interview, or a mock questions interview
company     view and validate researched company profiles
concepts    list every concept and how many questions it has
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path

from tutor import checklist as checklist_mod
from tutor import companies, mock, paths, prep as prep_mod, report
from tutor.bank import all_concept_keys, concepts_for, languages_in, load_bank, questions_for, split_key
from tutor.history import load_history, log_event, seen_counts
from tutor.practice import accepted_answers, normalize, solution_path
from tutor.runners import check_solution, starter_code
from tutor.scoring import concept_score, days_since, level_label, load_scores, record_result, save_scores
from tutor.session import choose_concept, lesson_path, suggest_questions


def build_parser():
    parser = argparse.ArgumentParser(prog="python -m tutor", description="AI Coding Teacher")
    sub = parser.add_subparsers(dest="command", required=True)

    nxt = sub.add_parser("next", help="pick the next concept and questions (used by /learn)")
    nxt.add_argument("--language", help="python (default), sql, javascript, or 'any'")
    nxt.add_argument("--concept", help="study this concept instead of the weakest one")
    nxt.add_argument("--prep", help="pick the most useful concept from a prep plan")
    nxt.add_argument("--review", action="store_true", help="the concept that is most overdue")
    nxt.add_argument("--quick", type=int, default=2, help="number of quick questions (default 2)")

    question = sub.add_parser("question", help="show one question without its answer")
    question.add_argument("id")
    question.add_argument("--hint", action="store_true", help="show the hint instead")

    check = sub.add_parser("check", help="test an answer or solution file")
    check.add_argument("id")
    check.add_argument("--answer", help="your answer to a quick question")
    check.add_argument("--file", help="solution file (default: the question's file in progress/solutions)")
    check.add_argument("--reveal", action="store_true", help="also show the explanation / reference solution")

    scores = sub.add_parser("scores", help="show your scores")
    scores.add_argument("--history", action="store_true", help="also show your recent answers")

    check = sub.add_parser("checklist", help="general interview topics")
    check.add_argument("action", nargs="?", choices=["show", "missing", "done", "undo"], default="show")
    check.add_argument("item", nargs="?", help="checklist id (for done / undo)")

    prep = sub.add_parser("prep", help="interview prep plans")
    prep.add_argument("action", choices=["new", "show", "list"])
    prep.add_argument("name", nargs="?")
    prep.add_argument("--file", help="path to a job description text file")
    prep.add_argument("--text", help="job description pasted as text")
    prep.add_argument("--company", help="company profile slug (see: company list)")

    mock_cmd = sub.add_parser("mock", help="mock interviews")
    mock_cmd.add_argument("kind", choices=["coding", "questions", "history"])
    mock_cmd.add_argument("--language", default="python")
    mock_cmd.add_argument("--count", type=int, help="number of problems / questions")
    mock_cmd.add_argument("--minutes", type=int, default=30, help="time limit for mock coding")
    mock_cmd.add_argument("--category", help="question tag, e.g. behavioral, databases, python")
    mock_cmd.add_argument("--prep", help="target a prep plan")

    company = sub.add_parser("company", help="company interview research")
    company.add_argument("action", choices=["list", "show", "validate"])
    company.add_argument("slug", nargs="?")

    record = sub.add_parser("record", help="log a result from outside the tutor")
    record.add_argument("--concept", help="language:concept, e.g. python:lists")
    record.add_argument("--tag", help="interview question tag, e.g. behavioral")
    record.add_argument("--qid", help="an id for the question (needed with --tag so repeats aren't double counted)")
    record.add_argument("--result", choices=["correct", "wrong"], required=True)
    record.add_argument("--difficulty", choices=["easy", "medium", "hard"], default="medium")
    record.add_argument("--weight", type=float, default=1.0)
    record.add_argument("--mode", default="record")

    sub.add_parser("concepts", help="list concepts and question counts")
    return parser


def find_question(bank, qid):
    for question in bank:
        if question["id"] == qid:
            return question
    raise SystemExit(f"No question with id {qid!r}. Run: python -m tutor next")


def cmd_next(args):
    """Print what the /learn skill needs to run one session on a concept."""
    bank, scores = load_bank(), load_scores()
    prep = prep_mod.load_prep(args.prep) if args.prep else None
    language = args.language or ("any" if args.concept else "python")
    lang, concept, reason = choose_concept(bank, scores, language, args.concept, prep, args.review)
    entry = scores.get(lang, {}).get(concept)
    score = concept_score(scores, lang, concept)
    print(f"concept: {lang}:{concept}")
    print(f"why: {reason}")
    last = f"{round(days_since(entry, datetime.now()), 1)} days ago" if entry else "never"
    print(f"score: {score} ({level_label(score)}), tried {entry['attempts'] if entry else 0} times, last practiced {last}")
    print(f"lesson: {lesson_path(lang, concept)}")
    questions = suggest_questions(bank, scores, seen_counts(load_history()), lang, concept, args.quick)
    print("questions (in order):")
    for q in questions:
        print(f"  {q['id']}  [{q['kind']}, {q['difficulty']}]")
    if not questions:
        print("  (none yet for this concept)")


def cmd_question(args):
    question = find_question(load_bank(), args.id)
    if args.hint:
        print(question.get("hint", "No hint written for this one. Break it into the smallest case first."))
        return
    print(f"{question['id']}  [{question['kind']}, {question['difficulty']}, {question['language']}:{question['concept']}]")
    print(question["prompt"])
    for letter, option in zip("abcdefgh", question.get("options", [])):
        print(f"   {letter}) {option}")
    if question["kind"] == "coding":
        path = solution_path(question)
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text(starter_code(question), encoding="utf-8")
        print(f"\nsolution file: {path}")


def cmd_check(args):
    question = find_question(load_bank(), args.id)
    if question["kind"] == "quick":
        if args.answer is None:
            raise SystemExit("Give --answer for a quick question.")
        correct = normalize(args.answer) in {normalize(a) for a in accepted_answers(question)}
        print("CORRECT" if correct else "INCORRECT")
        if args.reveal or correct:
            print("answer:", accepted_answers(question)[0])
            print("why:", question.get("explanation", ""))
        raise SystemExit(0 if correct else 1)

    path = Path(args.file) if args.file else solution_path(question)
    if not path.exists():
        raise SystemExit(f"No solution file at {path}. Run: python -m tutor question {question['id']}")
    result = check_solution(question, path.read_text(encoding="utf-8"))
    print("PASSED" if result.passed else "FAILED", f"({result.n_passed}/{result.n_total} tests)")
    if result.error:
        print("problem:", result.error)
    for failure in result.failures[:3]:
        print("failed:", failure)
    if result.output:
        print("your code printed:", result.output)
    if result.passed and question.get("complexity"):
        c = question["complexity"]
        print(f"typical complexity: time {c['time']}, space {c.get('space', '?')}")
    if args.reveal:
        print("\nreference solution:\n" + question["solution"])
    raise SystemExit(0 if result.passed else 1)


def cmd_scores(args):
    bank, scores = load_bank(), load_scores()
    print(report.format_scores(scores, bank))
    if args.history:
        print("\n" + report.format_history(load_history()))


def cmd_checklist(args):
    if args.action in ("done", "undo"):
        if not args.item:
            raise SystemExit("Name the checklist item, e.g. python -m tutor checklist done resume-walkthrough")
        checklist_mod.set_done(args.item, args.action == "done")
        print(f"Marked {args.item} as {'done' if args.action == 'done' else 'not done'}.")
        return
    data = checklist_mod.checklist_report(load_scores(), load_history(), mock.load_mocks(),
                                          len(prep_mod.list_preps()))
    print(checklist_mod.format_checklist(data, only_missing=args.action == "missing"))


def cmd_prep(args):
    bank, scores = load_bank(), load_scores()
    if args.action == "list":
        names = prep_mod.list_preps()
        print("\n".join(names) if names else "No prep plans yet. Try: python -m tutor prep new <name> --file jd.txt")
        return
    if not args.name:
        raise SystemExit("Give the plan a name, e.g. python -m tutor prep new shopify-intern --file jd.txt")
    if args.action == "show":
        print(prep_mod.format_plan(prep_mod.load_prep(args.name), scores, bank))
        return
    text = args.text or ""
    if args.file:
        text = open(args.file, encoding="utf-8").read()
    plan = prep_mod.create_prep(args.name, text, args.company)
    print(prep_mod.format_plan(plan, scores, bank))


def cmd_mock(args):
    plan = prep_mod.load_prep(args.prep) if args.prep else None
    if args.kind == "coding":
        mock.run_mock_coding(args.language, args.count or 2, args.minutes, plan)
    elif args.kind == "questions":
        mock.run_mock_questions(args.count or 5, args.category, plan)
    else:
        mocks = mock.load_mocks()
        if not mocks:
            print("No mock interviews yet.")
        for m in mocks[-10:]:
            print(f"{m['ts'][:16]}  {m['type']:<7} {m['solved']}/{m['total']} ({m['percent']}%)")


def cmd_company(args):
    bank = load_bank()
    from tutor.checklist import load_checklist
    keys = set(all_concept_keys(bank))
    ids = {item["id"] for item in load_checklist()}
    if args.action == "list":
        found = companies.list_companies()
        print("\n".join(found) if found else "No company research yet. Ask Claude: /company-research <company>")
        return
    slugs = [args.slug] if args.slug else companies.list_companies()
    for slug in slugs:
        profile = companies.load_company(slug)
        if profile is None:
            raise SystemExit(f"No profile for {slug!r}. Run: python -m tutor company list")
        if args.action == "show":
            print(companies.format_company(profile))
        else:
            problems = companies.validate_company(profile, keys, ids)
            print(f"{slug}: " + ("OK" if not problems else "\n  - " + "\n  - ".join(problems)))
            if problems:
                raise SystemExit(1)


def cmd_record(args):
    if not args.concept and not args.tag:
        raise SystemExit("Give --concept language:concept and/or --tag.")
    correct = args.result == "correct"
    event = {"mode": args.mode, "correct": correct, "difficulty": args.difficulty}
    if args.qid and not args.tag:
        event["qid"] = args.qid  # lets question rotation know this one was asked
    if args.concept:
        language, concept = split_key(args.concept)
        if concept not in concepts_for(load_bank(), language):
            raise SystemExit(f"Unknown concept {args.concept}. Run: python -m tutor concepts")
        scores = load_scores()
        record_result(scores, language, concept, correct, args.difficulty, args.weight)
        save_scores(scores)
        event.update(language=language, concept=concept)
    if args.tag:
        event.update(tag=args.tag, qid=args.qid or f"claude:{datetime.now().strftime('%Y%m%d%H%M%S')}")
    log_event(**event)
    print("Recorded.")


def cmd_concepts(args):
    bank = load_bank()
    for language in languages_in(bank):
        print(language)
        for concept in concepts_for(bank, language):
            quick = len(questions_for(bank, language, concept, "quick"))
            coding = len(questions_for(bank, language, concept, "coding"))
            print(f"  {language}:{concept:<28} {quick} quick, {coding} coding")


COMMANDS = {"next": cmd_next, "question": cmd_question, "check": cmd_check, "scores": cmd_scores, "checklist": cmd_checklist, "prep": cmd_prep, "mock": cmd_mock,
            "company": cmd_company, "record": cmd_record, "concepts": cmd_concepts}


def main(argv=None):
    # Windows consoles can choke on the symbols in lessons when output is piped; force UTF-8.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    args = build_parser().parse_args(argv)
    try:
        COMMANDS[args.command](args)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
