'''
>>> from student_module import student_function
>>> student_function('example')
Traceback (most recent call last):
    ...
ValueError
'''

from test_util import test
import doctest


@test()
def test_passed(test_feedback):
    failure_count, test_count = doctest.testmod(optionflags=doctest.FAIL_FAST)
    return failure_count == 0
    

# Put the above in the ZyLab unit test.
# Here's how to run the test locally to see how it works:
import io
test_feedback = io.StringIO()
print(test_passed(test_feedback))
print(test_feedback.getvalue())
