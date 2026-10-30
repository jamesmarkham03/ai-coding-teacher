import unittest

from tutor.bank import load_bank
from tutor.practice import big_o_of, normalize
from tutor.runners import check_solution, extension_for, starter_code

BANK = {q["id"]: q for q in load_bank()}


class PythonRunnerTests(unittest.TestCase):
    def test_wrong_answer_reports_which_input_failed(self):
        result = check_solution(BANK["py-lists-c1"], "def remove_duplicates(nums):\n    return nums")
        self.assertFalse(result.passed)
        self.assertEqual((result.n_passed, result.n_total), (1, 3))  # only the empty list passes untouched
        self.assertIn("expected [1, 2, 3]", result.failures[0])

    def test_syntax_error_is_reported_not_raised(self):
        result = check_solution(BANK["py-lists-c1"], "def remove_duplicates(nums)\n    return nums")
        self.assertFalse(result.passed)
        self.assertIn("SyntaxError", result.error)

    def test_missing_function_is_reported(self):
        result = check_solution(BANK["py-lists-c1"], "def something_else():\n    pass")
        self.assertIn("must define `remove_duplicates`", result.error)

    def test_infinite_loop_times_out(self):
        result = check_solution(BANK["py-lists-c1"], "def remove_duplicates(nums):\n    while True:\n        pass", timeout=1)
        self.assertIn("Timed out", result.error)

    def test_exception_in_student_code_becomes_a_failure_message(self):
        result = check_solution(BANK["py-lists-c1"], "def remove_duplicates(nums):\n    return nums[99]")
        self.assertFalse(result.passed)
        self.assertIn("IndexError", result.failures[0])

    def test_printed_output_is_captured_for_the_student(self):
        code = "def remove_duplicates(nums):\n    print('debugging')\n    return nums"
        self.assertIn("debugging", check_solution(BANK["py-lists-c1"], code).output)

    def test_unordered_and_outer_unordered_comparisons(self):
        shuffled = ("def group_anagrams(words):\n"
                    "    groups = {}\n"
                    "    for w in words:\n"
                    "        groups.setdefault(''.join(sorted(w)), []).append(w)\n"
                    "    return [g[::-1] for g in list(groups.values())[::-1]]")
        self.assertTrue(check_solution(BANK["py-dictionaries-c4"], shuffled).passed)  # group order is free
        perms = "def permutations(nums):\n    import itertools\n    return [list(p) for p in itertools.permutations(nums)][::-1]"
        self.assertTrue(check_solution(BANK["py-recursion-c3"], perms).passed)

    def test_tree_and_linked_list_adapters(self):
        tree = "def max_depth(root):\n    return 0 if root is None else 1 + max(max_depth(root.left), max_depth(root.right))"
        self.assertTrue(check_solution(BANK["py-trees-c1"], tree).passed)
        wrong_list = "def middle_node(head):\n    return head"
        self.assertFalse(check_solution(BANK["py-linked-lists-c3"], wrong_list).passed)

    def test_class_questions_call_methods_in_order(self):
        broken = ("class Counter:\n    def __init__(self):\n        self.n = 0\n"
                  "    def increment(self):\n        self.n += 2\n"
                  "    def decrement(self):\n        self.n -= 1\n    def value(self):\n        return self.n")
        self.assertFalse(check_solution(BANK["py-classes-c1"], broken).passed)


class SqlRunnerTests(unittest.TestCase):
    def test_correct_query_passes_and_row_order_is_ignored_when_unordered(self):
        q = BANK["sql-select-filter-c2"]
        self.assertTrue(check_solution(q, "SELECT DISTINCT position FROM players ORDER BY position DESC;").passed)

    def test_order_matters_when_the_question_is_ordered(self):
        q = BANK["sql-select-filter-c1"]
        self.assertFalse(check_solution(q, "SELECT name FROM players WHERE team = 'Comets' ORDER BY name DESC").passed)

    def test_bad_sql_gives_a_readable_error(self):
        result = check_solution(BANK["sql-select-filter-c1"], "SELEC name FROM players")
        self.assertIn("SQL error", result.error)

    def test_untouched_starter_asks_for_a_query(self):
        q = BANK["sql-select-filter-c1"]
        self.assertIn("Write your query", check_solution(q, starter_code(q)).error)


class JavaScriptRunnerTests(unittest.TestCase):
    def test_passing_and_failing_javascript(self):
        q = BANK["js-arrays-c1"]
        self.assertTrue(check_solution(q, "function sumEvens(nums) { return nums.filter(n => n % 2 === 0).reduce((a, b) => a + b, 0); }").passed)
        result = check_solution(q, "function sumEvens(nums) { return 0; }")
        self.assertFalse(result.passed)
        self.assertIn("expected 6", result.failures[0])

    def test_javascript_class_and_load_error(self):
        q = BANK["js-functions-classes-c2"]
        self.assertFalse(check_solution(q, "class Stack { constructor() {} }").passed)
        self.assertIn("must define", check_solution(q, "const nothing = 1;").error)

    def test_javascript_syntax_error_and_timeout(self):
        q = BANK["js-arrays-c1"]
        self.assertTrue(check_solution(q, "function sumEvens( {").error)
        self.assertIn("Timed out", check_solution(q, "function sumEvens(nums) { while (true) {} }", timeout=2).error)


class HelperTests(unittest.TestCase):
    def test_starter_code_contains_prompt_and_signature(self):
        text = starter_code(BANK["py-lists-c3"])
        self.assertIn("# Write rotate_list", text)
        self.assertIn("def rotate_list(nums, k):", text)
        self.assertTrue(starter_code(BANK["js-arrays-c1"]).count("function sumEvens(nums)"))
        self.assertEqual(extension_for("sql"), ".sql")

    def test_normalize_and_big_o_parsing(self):
        self.assertEqual(normalize(" 'Ell' "), "ell")
        self.assertEqual(big_o_of("It's O( n log n )"), "o(nlogn)")
        self.assertEqual(big_o_of("O(n) time, O(1) space"), "o(n)")
        self.assertIsNone(big_o_of("linear"))


if __name__ == "__main__":
    unittest.main()
