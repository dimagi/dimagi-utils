#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from __future__ import absolute_import
import os, re, traceback, sys
from django.conf import settings
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.contrib.sites.models import Site
import json
from dimagi.utils.parsing import json_format_datetime
from datetime import date, datetime
from decimal import Decimal


def get_url_base():
    try:
        protocol = settings.DEFAULT_PROTOCOL
    except:
        protocol = 'http'
    return '%s://%s' % (protocol, Site.objects.get(id = settings.SITE_ID).domain)


def get_secure_url_base():
    return 'https://%s' % Site.objects.get(id = settings.SITE_ID).domain


def parse_int(arg_keys=[], kwarg_keys=[]):
    """
    A decorator to translate coerce arguments to be ints

    >>> @parse_int([0,1])
    >>> def add(x,y):
    ...     return x + y
    ...
    >>> add("1", "2")
    3

    """
    def _parse_int(fn):
        def _fn(*args, **kwargs):
            args = list(args)
            kwargs = dict(kwargs)
            for i in arg_keys:
                args[i] = int(args[i])
            for key in kwarg_keys:
                kwargs[key] = int(kwargs[key])
            return fn(*args, **kwargs)
        return _fn
    return _parse_int

# http://stackoverflow.com/questions/455580/json-datetime-between-python-and-javascript
def json_handler(obj):
    if callable(getattr(obj, 'to_complete_json', None)):
        return obj.to_complete_json()
    elif callable(getattr(obj, 'to_json', None)):
        return obj.to_json()
    elif isinstance(obj, datetime):
        return json_format_datetime(obj)
    elif isinstance(obj, date):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        return float(obj) # warning, potential loss of precision
    else:
        return json.JSONEncoder().default(obj)

def json_response(obj, **kwargs):
    if not kwargs.has_key('default'):
        kwargs['default'] = json_handler
    return HttpResponse(json.dumps(obj, **kwargs), mimetype="application/json")

def json_request(params, lenient=True):
    d = {}
    for key, val in params.items():
        try:
            d[str(key)] = json.loads(val)
        except ValueError:
            if lenient:
                d[str(key)] = val
            else:
                raise
    return d


# get_ip was stolen verbatim from auditcare.utils
# this is not intended to be an all-knowing IP address regex
IP_RE = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')

def get_ip(request):
    """
    Retrieves the remote IP address from the request data.  If the user is
    behind a proxy, they may have a comma-separated list of IP addresses, so
    we need to account for that.  In such a case, only the first IP in the
    list will be retrieved.  Also, some hosts that use a proxy will put the
    REMOTE_ADDR into HTTP_X_FORWARDED_FOR.  This will handle pulling back the
    IP from the proper place.
    """

    # if neither header contain a value, just use local loopback
    ip_address = request.META.get('HTTP_X_FORWARDED_FOR',
        request.META.get('REMOTE_ADDR', '127.0.0.1'))
    if ip_address:
        # make sure we have one and only one IP
        try:
            ip_address = IP_RE.match(ip_address)
            if ip_address:
                ip_address = ip_address.group(0)
            else:
                # no IP, probably from some dirty proxy or other device
                # throw in some bogus IP
                ip_address = '10.0.0.1'
        except IndexError:
            pass
    return ip_address
