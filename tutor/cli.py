"""Command line entry point:  python -m tutor <command>

learn       teach -> practice -> question on one concept (picks your weakest by default)
scores      per-concept and per-language scores, due reviews, what to do next
checklist   general interview topics: covered vs missed
prep        build a study plan from a job description or company
mock        timed mock coding interview, or a mock questions interview
company     view and validate researched company profiles
record      log a result from outside the tutor (used by the Claude skills)
concepts    list every concept and how many questions it has
"""
import argparse
import sys
from datetime import datetime

from tutor import checklist as checklist_mod
from tutor import companies, mock, paths, prep as prep_mod, report
from tutor.bank import all_concept_keys, concepts_for, languages_in, load_bank, questions_for, split_key
from tutor.history import load_history, log_event
from tutor.scoring import load_scores, record_result, save_scores
from tutor.session import run_learn


def build_parser():
    parser = argparse.ArgumentParser(prog="python -m tutor", description="AI Coding Teacher")
    sub = parser.add_subparsers(dest="command", required=True)

    learn = sub.add_parser("learn", help="teach, practice, question on one concept")
    learn.add_argument("--language", help="python (default), sql, javascript, or 'any'")
    learn.add_argument("--concept", help="study this concept instead of the weakest one")
    learn.add_argument("--prep", help="pick the most useful concept from a prep plan")
    learn.add_argument("--review", action="store_true", help="refresh the concept that is most overdue (no lesson)")
    learn.add_argument("--quick", type=int, default=2, help="number of quick questions (default 2)")

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


COMMANDS = {"scores": cmd_scores, "checklist": cmd_checklist, "prep": cmd_prep, "mock": cmd_mock,
            "company": cmd_company, "record": cmd_record, "concepts": cmd_concepts}


def main(argv=None):
    # Windows consoles can choke on the symbols in lessons when output is piped; force UTF-8.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    args = build_parser().parse_args(argv)
    if args.command == "learn":
        args.language = args.language or ("any" if args.concept else "python")
        try:
            run_learn(args)
        except KeyboardInterrupt:
            print("\nSession stopped. Nothing from the unfinished question was saved.")
        return
    try:
        COMMANDS[args.command](args)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
