import hashlib
import json
from django.core.cache import cache

def cached_view(db, view_name, view_kwargs, timeout=60):
    """
    Returns cached view results from couch. Makes no attempts at invalidation
    so only use this if you are absolutely sure you can serve some stale data.

    This is meant to be a much lighter-weight, simpler alternative to the more
    advanced functionality found in cache_core.
    """
    cache_key = '{db}-{view}-{args}'.format(
        db=db.uri,
        view=view_name,
        args=hashlib.md5(json.dumps(view_kwargs, sort_keys=True)).hexdigest(),
    )
    MISSING = 'MISSING'
    res = cache.get(cache_key, MISSING)
    if res != MISSING:
        return res
    else:
        res = db.view(view_name,
            **view_kwargs
        ).all()
        cache.set(cache_key, res, timeout)
        return res

