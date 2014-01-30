from .classproperty import classproperty
from .datespan import datespan_in_request
from .lazy_property import lazy_property
from .log_exception import log_exception
from .memoized import memoized
from .profile import profile
from .view import get_file


def inline(fn):
    """
    decorator used to call a function in place
    similar to JS `var user_id = (function () { ... }());`

    example:

        @inline
        def user_id():
            if request.couch_user.is_commcare_user():
                return request.couch_user.get_id
            else:
                return request.GET.get('user_id')

    """
    return fn()
