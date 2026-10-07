from unittest import TestCase
from prim.exec import exec

class TestExec(TestCase):
    def test_exec_crash(self):
        with self.assertRaises(ZeroDivisionError):
            exec("(/ 1 0)")
    
    def test_exec_factorial(self):
        source_code = """
        (
          (lambda (factorial)
            (factorial factorial 5)
          )
          (lambda (factorial n)
            (if (= n 0)
              1
              (* n (factorial factorial (- n 1)))
            )
          )
        )
        """
        self.assertEqual([120], exec(source_code))

    def test_exec_factorial_with_define(self):
        source_code = """
        (define factorial
          (lambda (n)
            (if (= n 0)
              1
              (* n (factorial (- n 1)))
            )
          )
        )
        (factorial 5)
        """
        self.assertEqual(["<DEFINITION(S) ADDED>", 120], exec(source_code))

    def test_exec_if(self):
        source_code = """
        (if 
          false 1
          (and (< 1 2) (< 1 3)) 2
          3
        )
        """
        self.assertEqual([2], exec(source_code))

    def test_exec_call_preserves_caller_binding(self):
        source_code = """
        (define x 10)
        ((lambda (x) x) 20)
        x
        """
        self.assertEqual(["<DEFINITION(S) ADDED>", 20, 10], exec(source_code))

    def test_exec_call_does_not_leak_parameter(self):
        source_code = """
        (define identity (lambda (x) x))
        (identity 20)
        x
        """
        with self.assertRaises(RuntimeError):
            exec(source_code)

    def test_exec_returned_closure_keeps_captured_binding(self):
        source_code = """
        (define make_adder (lambda (x) (lambda (y) (+ x y))))
        (define add_ten (make_adder 10))
        (define x 100)
        (add_ten 5)
        x
        """
        self.assertEqual(
            ["<DEFINITION(S) ADDED>"] * 3 + [15, 100],
            exec(source_code),
        )

    
    def test_exec_math(self):
        source_code = "(+ 1 (* (- -2.1 3.14) 4))"
        self.assertEqual([-19.96], exec(source_code))

    def test_exec_arithmetic_rejects_booleans(self):
        with self.assertRaises(RuntimeError):
            exec("(+ true 1)")
        with self.assertRaises(RuntimeError):
            exec("(+ 1 false)")

    def test_exec_numeric_comparisons_reject_booleans(self):
        with self.assertRaises(RuntimeError):
            exec("(= true 1)")
        with self.assertRaises(RuntimeError):
            exec("(= 1 false)")
    
    def test_exec_string(self):
        source_code = """
        (
          (lambda (x) x)
          "i'm a raw string... here comes a backslash: \... here come a tab:	... and now an emoji: 🤓... and now some korean: 김치"
        )
        """
        self.assertEqual(
            ["i'm a raw string... here comes a backslash: \... here come a tab:	... and now an emoji: 🤓... and now some korean: 김치"],
            exec(source_code)
        )

    def test_exec_string_concat(self):
        self.assertEqual(["hello"], exec('(++ "hell" "o")'))

    def test_exec_list(self):
        self.assertEqual(
            [2],
            exec("(head (rest (:: 1 (:: 2 (:: 3 (empty))))))")
        )
    
    def test_exec_list_empty_predicate(self):
        source_code = """
        (empty? (empty))
        (empty? (:: 1 (empty)))
        (empty? (rest (:: 1 (empty))))
        """
        self.assertEqual([True, False, True], exec(source_code))

    def test_exec_list_empty_predicate_rejects_invalid_arguments(self):
        with self.assertRaises(RuntimeError):
            exec("(empty?)")
        with self.assertRaises(RuntimeError):
            exec("(empty? (empty) (empty))")
        with self.assertRaises(RuntimeError):
            exec("(empty? 0)")

    def test_exec_list_traversal(self):
        source_code = """
        (define sum (lambda (xs)
          (if (empty? xs) 0
            (+ (head xs) (sum (rest xs))))))
        (sum (:: 1 (:: 2 (empty))))
        (sum (empty))
        """
        self.assertEqual(["<DEFINITION(S) ADDED>", 3, 0], exec(source_code))

    def test_exec_multiple_expressions(self):
        source_code = """
        (head (rest (:: 1 (:: 2 (:: 3 (empty))))))
        (if 
          false 1
          (and (< 1 2) (< 1 3)) 2
          3
        )
        """
        self.assertEqual([2, 2], exec(source_code))
