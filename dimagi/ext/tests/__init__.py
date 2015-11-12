import os
import sys

if "django.conf" not in sys.modules:
    # configure django settings for nosetests
    from django.conf import settings
    settings.configure(
        UNIT_TESTING=True,
        SECRET_KEY="secret",
    )
else:
    from .test_attachments import *
    from .test_blobdb import *
    from .test_jsonobject import *
