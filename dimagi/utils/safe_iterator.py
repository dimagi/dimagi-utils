from functools import wraps


class IteratorAlreadyConsumedException(Exception):
    pass


class SafeIterator(object):
    """
    This iterator-like object wraps an iterator.
    The SafeIterator will raise a IteratorAlreadyConsumedException if a user attempts to iterate through it a
    second time.
    This is useful if the wrapped iterator is a one time user generator, which would simply raise StopIteration
    exception again (thereby, appearing "empty" to a user who didn't realize that the generator had already been
    consumed).

    Note that this class cannot be used interchangeably with an iterator, because iterators must raise
    StopIteration exceptions on subsequent iterations. However, in practice, I don't expect this to be an issue.
    https://docs.python.org/2/library/stdtypes.html#iterator-types
    """
    def __init__(self, generator):
        """
        Create a new SafeIterator by wrapping a normal generator (or iterator)
        :param generator: the generator to be wrapped
        """
        self._generator = generator
        self._has_been_consumed = False

    def __iter__(self):
        return self

    def next(self):
        if self._has_been_consumed:
            raise IteratorAlreadyConsumedException
        try:
            return self._generator.next()
        except StopIteration as e:
            self._has_been_consumed = True
            raise

    def __next__(self):
        # Python 3 compatibility
        return self.next()


def safe_generator(fn):
    """
    This decorator function wraps the return value of the given function in a SafeIterator.
    You should only use this decorator on functions that return generators.
    The SafeIterator will render the generator "safe" by raising a IteratorAlreadyConsumedException if it is
    iterated a second time.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        return SafeIterator(fn(*args, **kwargs))
    return wrapper
