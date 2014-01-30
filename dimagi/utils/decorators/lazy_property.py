class lazy_property(object):
    """
    Shamelessly pulled from the werkzeug utils' cached property:
    https://github.com/mitsuhiko/werkzeug/blob/master/werkzeug/utils.py#L35
    renamed to lazy_property to avoid confusion with our memoized decorator

    A decorator that converts a function into a lazy property. The
    function wrapped is called the first time to retrieve the result
    and then that calculated result is used the next time you access
    the value::

    Replaces this:

        class Foo(object):
            _foo = None

            @property
            def foo(self):
                if self._foo is None:
                    # calculate something important here
                    self._foo = 42
                return self._foo

    with this:

        class Foo(object):

            @lazy_property
            def foo(self):
                # calculate something important here
                return 42

    The class has to have a `__dict__` in order for this property to
    work.
    """

    # implementation detail: this property is implemented as non-data
    # descriptor. non-data descriptors are only invoked if there is
    # no entry with the same name in the instance's __dict__.
    # this allows us to completely get rid of the access function call
    # overhead. If one choses to invoke __get__ by hand the property
    # will still work as expected because the lookup logic is replicated
    # in __get__ for manual invocation.

    def __init__(self, func, name=None, doc=None):
        self.__name__ = name or func.__name__
        self.__module__ = func.__module__
        self.__doc__ = doc or func.__doc__
        self.func = func

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        value = obj.__dict__.get(self.__name__, 'nothing')
        if value is 'nothing':
            value = self.func(obj)
            obj.__dict__[self.__name__] = value
        return value
