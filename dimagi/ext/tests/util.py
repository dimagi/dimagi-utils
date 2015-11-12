from unittest import TestCase

def generate_cases(argsets, cls=None):
    """Generate a set of parameterized test cases

    Until we have nose generator tests...

    Note: generated test cases cannot be run individually by name since
    their parameterized names are not valid function names. This was a
    tradeoff with making parameterized tests identifiable on failure.

    :param argsets: A sequence of argument tuples or dicts, one for each
    test case to be generated.
    :param cls: Optional test case class to which tests should be added.
    """
    def add_cases(test_func):
        if cls is None:
            class Test(TestCase):
                pass
            Test.__name__ = test_func.__name__
        else:
            Test = cls

        for args in argsets:
            def test(self, args=args):
                if isinstance(args, dict):
                    return test_func(self, **args)
                return test_func(self, *args)

            test.__name__ = test_func.__name__ + repr(args)
            assert not hasattr(Test, test.__name__), \
                "duplicate test case: {} {}".format(Test, test.__name__)

            setattr(Test, test.__name__, test)

        if cls is None:
            # Only return newly created test class; otherwise nose will
            # run tests on cls twice. Explanation: the returned value
            # will be bound to the name of the decorated test_func; if
            # cls is provided then there will be two names bound to the
            # same test class
            return Test

    return add_cases
