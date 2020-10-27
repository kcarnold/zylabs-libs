import builtins
import io
import re
import sys
import traceback
from contextlib import redirect_stdout


class TestFailure(AssertionError):
    pass


def test(input="", show_stdout=True):
    """
    Decorator for the ZyLabs test_passed function that:
    
    * Turns AssertionErrors into test feedback
    * Catches syntax and other errors
    * Allows providing arbitrary input (and fails if input() is called but no input was provided)
    * Captures standard output.
    * Has the test fail on any errors, pass otherwise.
    * Interprets `None` returns as passing.
    
    This can wrap an existing test_passed function unchanged also.
    
    Usage:
    @test(input='abc')
    def test_passed(test_feedback):
        from student_code import func
        result = func(input)
        assert result == 1, "Result should equal 1"
        assert sys.stdout.getvalue() == '', "Code should not print any output"
    """

    def wrapper(f):
        def test_passed(test_feedback):
            sys.stdin = io.StringIO(input)
            stdout = io.StringIO()

            our_feedback = io.StringIO()

            if input == "":

                def input_override(*a):
                    raise TestFailure(
                        "This task should not ask for user input. Comment out or remove any calls to 'input'"
                    )

                builtins.input = input_override

            try:
                with redirect_stdout(stdout):
                    result = f(our_feedback)
                our_feedback_val = our_feedback.getvalue()
                test_feedback.write(our_feedback_val)
                # Show the actual output.
                if show_stdout:
                    sys.stdout.write(stdout.getvalue())
                if result is None:
                    result = True
                if result:
                    # If the test didn't write a warning, write "Passed!"
                    if len(our_feedback_val) == 0:
                        test_feedback.write("Passed!\n")
                return result
            except TestFailure as e:
                test_feedback.write(str(e))
                return False
            except AssertionError as e:
                assertion_err = str(e).strip()
                num_frames = len(traceback.extract_tb(sys.exc_info()[2]))
                if num_frames == 2:
                    # This assertion is from our test code,
                    # not from the user's code.
                    # How can we tell? There's only 2 stack frames:
                    # zyLabsUnitTest (our test code) and the call within this function.
                    test_feedback.write(assertion_err)
                else:
                    if assertion_err:
                        test_feedback.write("Assertion failed: " + assertion_err)
                    else:
                        test_feedback.write("Error running your code:")
                    test_feedback.write(
                        "\n\n" + traceback.format_exc()
                    )
                return False
            except:
                test_feedback.write(
                    "Error running your code:\n\n" + traceback.format_exc()
                )
                return False

        return test_passed

    return wrapper


def function_testcase(module_name, function_name, *, args, expected_result):
    import importlib

    @test()
    def test_passed(test_feedback):
        module = importlib.import_module(module_name)
        if not hasattr(module, function_name):
            raise TestFailure("Missing function {}".format(function_name))
        func = getattr(module, function_name)
        result = func(*args)
        if result == expected_result:
            return True
        pretty_args = repr(tuple(args)) if len(args) != 1 else "({!r})".format(args[0])
        raise TestFailure(
            "{}{} should return {!r}.".format(
                function_name, pretty_args, expected_result
            )
        )

    return test_passed


guard_line_re = re.compile(
    r'^if\s+__name__\s*==\s*[\'"]__main__[\'"]\s*:', re.MULTILINE
)

if __name__ == "__main__":
    assert guard_line_re.match('if __name__ == "__main__":')
    assert guard_line_re.match("if __name__ == '__main__':")
    assert guard_line_re.match("if __name__=='__main__'  :")
    assert guard_line_re.match("if __name__=='__main__':")
    assert not guard_line_re.match("if __name__ == __main__:")
    assert not guard_line_re.match("if __main__ == '__name__':")

    assert guard_line_re.search('\n\nif __name__ == "__main__":\n    print("test")\n')

    @test(input="abc")
    def test_passed(test_feedback):
        assert 1 == 0, "1 should equal 0"

    test_feedback = io.StringIO()
    assert test_passed(test_feedback) is False
    assert test_feedback.getvalue() == "1 should equal 0"
