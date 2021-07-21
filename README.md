# zylabs-libs
Utility code for ZyBooks autograders in Python

## `test_util.py`

Add `test_util.py` as an "additional file" in the test. Then just add a decorator to your `test_passed` function for instant upgrades:

* Turns `AssertionError`s into test feedback
* Catches syntax and other errors
* Allows providing arbitrary input (and fails if `input()` is called but no input was provided)
* Captures standard output.
* Has the test fail on any errors, pass otherwise.
* Interprets `None` returns as passing.

Example unit test:

```python
from test_util import test

@test()
def test_passed(test_feedback):
    from fraction import Fraction
    f1 = Fraction(1, 2)
    f2 = Fraction(2, 3)
    f3 = f1 * f2
    assert isinstance(f3, Fraction), "__mul__ should return a Fraction."
    assert str(f3) == '1/3', "1/2 * 2/3 should equal 1/3."
    assert f1.numerator == 1 and f1.denominator == 2, "__mul__ should not change 'self'."
    assert f2.numerator == 2 and f2.denominator == 3, "__mul__ should not change the other fraction."
```

## doctests

Students sometimes have trouble with the unit tests because they don't know how to reproduce a failure.
The Python standard library has a solution for this: [doctests](https://docs.python.org/3/library/doctest.html).
I've been trying this out with ZyLabs; see `doctest_example.py` for an example of how to write a unit test that's actually a doctest.

I don't think it'll run any doctests that students write, but that would be a nifty extension (to be able to test their tests, for example).
