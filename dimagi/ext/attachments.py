from __future__ import absolute_import
from cStringIO import StringIO
from os.path import join

from couchdbkit.exceptions import InvalidAttachment, ResourceNotFound
from dimagi.ext.blobdb import NotFound


class BlobMixin(object):

    def _blobdb_bucket(self):
        return join(type(self).__name__, self._doc["_id"])

    def put_attachment(self, content, name=None, content_type=None, content_length=None):
        """Put attachment in blob database

        :param content: String or file object.
        """
        db = get_blob_db(self)

        # TODO store name in couch document. Without it we cannot
        # enumerate attachments by name. Do we need that?
        # Is it important to keep content type and content length?

        if name is None:
            name = getattr(content, "name", None)
        if name is None:
            raise InvalidAttachment("cannot save attachment without name")

        if isinstance(content, unicode):
            content = StringIO(content.encode("utf-8"))

        db.put(content, name, self._blobdb_bucket())
        return True

    def fetch_attachment(self, name, stream=False):
        """Get named attachment

        :param stream: When true, return a file-like object that can be
        read at least once (streamers should not expect to seek within
        or read the contents of the returned file more than once).
        """
        db = get_blob_db(self)
        try:
            blob = db.get(name, self._blobdb_bucket())
        except NotFound:
            raise ResourceNotFound(u"{model} attachment: {name!r}".format(
                model=type(self).__name__,
                name=name,
            ))
        if stream:
            return blob

        with blob:
            body = blob.read()
        try:
            body = body.decode("utf-8", "strict")
        except UnicodeDecodeError:
            # Return bytes on decode failure, otherwise unicode.
            # Ugly, but consistent with restkit.wrappers.Response.body_string
            pass
        return body

    def delete_attachment(self, name):
        db = get_blob_db(self)
        return db.delete(name, self._blobdb_bucket())


def get_blob_db(couch_model):
    try:
        return couch_model._blobdb
    except AttributeError:
        pass
    from django.conf import settings
    raise NotImplementedError
