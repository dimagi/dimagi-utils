from __future__ import absolute_import
from cStringIO import StringIO
from os.path import join

from couchdbkit.exceptions import InvalidAttachment, ResourceNotFound
from dimagi.ext.blobdb import FilesystemBlobDB, NotFound
from dimagi.ext.couchdbkit import (
    DocumentSchema,
    DictProperty,
    IntegerProperty,
    StringProperty,
)
from django.conf import settings
from jsonobject import JsonObject


class BlobMeta(DocumentSchema):
    content_type = StringProperty()
    content_length = IntegerProperty()


class BlobMixin(JsonObject):

    blobs = DictProperty(BlobMeta)

    def _blobdb_bucket(self):
        if self._id is None or self._rev is None:
            raise ResourceNotFound("cannot manipulate attachment on unsaved document")
        return join(self.doc_type, self._id)

    def put_attachment(self, content, name=None, content_type=None, content_length=None):
        """Put attachment in blob database

        :param content: String or file object.
        """
        db = get_blob_db()

        if name is None:
            name = getattr(content, "name", None)
        if name is None:
            raise InvalidAttachment("cannot save attachment without name")

        if isinstance(content, unicode):
            content = StringIO(content.encode("utf-8"))
        elif isinstance(content, bytes):
            content = StringIO(content)

        # do we need to worry about BlobDB reading beyond content_length?
        bucket = self._blobdb_bucket()
        content_length = db.put(content, name, bucket)
        self.blobs[name] = BlobMeta(
            content_type=content_type,
            content_length=content_length,
        )
        return True

    def fetch_attachment(self, name, stream=False):
        """Get named attachment

        :param stream: When true, return a file-like object that can be
        read at least once (streamers should not expect to seek within
        or read the contents of the returned file more than once).
        """
        db = get_blob_db()
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
        db = get_blob_db()
        return db.delete(name, self._blobdb_bucket())


_blob_db = [] # singleton/global, stack for tests to push temporary dbs

def get_blob_db():
    if not _blob_db:
        db = FilesystemBlobDB(settings.SHARED_DRIVE_CONF.blob_dir)
        _blob_db.append(db)
    return _blob_db[-1]
