import ast
import builtins
import io
import re
import sys
import traceback
from contextlib import redirect_stdout


class TestFailure(AssertionError):
    pass


def format_tb(exc_info):
    """Accepts *sys.exc_info()."""
    tbe = traceback.TracebackException(*exc_info)
    if "test_util.py" in tbe.stack[0].filename:
        del tbe.stack[0]
    return "".join(tbe.format(chain=True))


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
                if result is None:
                    result = True
                if len(our_feedback_val) == 0:
                    # If the test didn't write something, write something here.
                    if result:
                        test_feedback.write("Passed!\n")
                    else:
                        test_feedback.write("Test didn't pass. Some message should have been reported but didn't; please alert the course staff.")
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
                    test_feedback.write("\n\n" + format_tb(sys.exc_info()))
                return False
            except:
                tb = format_tb(sys.exc_info())
                tb = tb.replace(
                    "/home/runner/local/submission/unit_test_student_code/", ""
                )
                test_feedback.write("Error running your code:\n\n" + tb)
                return False
            finally:
                # Show the actual output.
                if show_stdout:
                    sys.stdout.write(stdout.getvalue())

        return test_passed

    return wrapper

def doctester(module_name, total_points=1):
    '''
    Usage:
    
    Start with a triple-quoted doctest session. Then:

    from test_util import doctester
    test_passed = doctester("credit_card", total_points=3)
    '''
    import doctest, sys, importlib

    testcase_module = sys.modules['zyLabsUnitTest']
    testcase_module.__file__ = 'zyLabsUnitTest.py'

    @test()
    def test_passed(test_feedback):
        target_module = importlib.import_module(module_name)
        #assert sys.stdout.getvalue() == '', "Please comment out any input or print statements when submitting."
        failure_count, test_count = doctest.testmod(
            testcase_module,
            extraglobs=target_module.__dict__,
            optionflags=doctest.DONT_ACCEPT_TRUE_FOR_1 | doctest.ELLIPSIS, # doctest.FAIL_FAST
            name="zyBooks_test",
            report=True,
            verbose=False
        )
        return total_points * (1 - (failure_count / test_count))
    return test_passed


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


def get_global_refs(callable):
    # Get inside any wrappers, like bound method objects.
    while hasattr(callable, "__func__"):
        callable = callable.__func__

    import inspect
    return inspect.getclosurevars(callable).globals.keys()

def filenames_test(*filenames):
    """
    Example usage:
    
    import test_util
    test_passed = test_util.filenames_test("submission_file.py")
    """
    def test_passed(test_feedback):
        for FILENAME in filenames:
            try:
                source = open(FILENAME).read()
                parsed = ast.parse(source, filename=FILENAME)
                docstring = ast.get_docstring(parsed)
            except SyntaxError:
                test_feedback.write(traceback.format_exc(limit=0))
                return False
            except:
                test_feedback.write("Unknown error reading documentation. Ask the course staff for help.\n\n" + traceback.format_exc())

            if docstring is None or not any(x in docstring for x in ['\nAuthor', 'Author:', '@author']):
                test_feedback.write(FILENAME + " documentation should include author (see the template).")
                return False

            if any(x in docstring for x in ['YOUR-NAME', 'yn123', 'PARTNER-NAME', 'pn31']):
                test_feedback.write(FILENAME + ": Please replace the template names and usernames with your own.")
                return False

            if any(x in docstring for x in ["Describe the module here.", "Lab X.X"]):
                test_feedback.write(FILENAME + ": Please replace the template documentation with your own.")
                return False
            
        test_feedback.write("Passed!")
        return True
    return test_passed

name_test = names_test = filenames_test


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
