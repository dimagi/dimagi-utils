"""Filesystem database for large binary data objects (blobs)
"""
from __future__ import absolute_import
import os
import shutil
from hashlib import md5
from os.path import exists, isdir, dirname, join


CHUNK_SIZE = 4096
DEFAULT_BUCKET = "_default"


class FilesystemBlobDB(object):
    """Filesystem storage for large binary data objects
    """

    def __init__(self, rootdir):
        self.rootdir = rootdir

    def put(self, content, name, bucket=DEFAULT_BUCKET):
        """Put a blob in persistent storage

        :param content: A file-like object in binary read mode.
        :param name: The name of the object to be saved.
        :param bucket: Optional bucket name used to partition blob data
        in the persistent storage medium. This may be delimited with
        file path separators. Nested directories will be created for
        each logical path element, so it must be a valid relative path.
        Blob names within a single bucket must be unique.
        """
        path = self._getpath(name, bucket)
        dirpath = dirname(path)
        if not isdir(dirpath):
            os.makedirs(dirpath)
        with open(path, "wb") as fh:
            while True:
                chunk = content.read(CHUNK_SIZE)
                if not chunk:
                    break
                fh.write(chunk)

    def get(self, name, bucket=DEFAULT_BUCKET):
        """Get a blob

        :param name: The name of the object to get.
        :param bucket: Optional bucket name. This must have the same
        value that was passed to ``put``.
        :returns: A file-like object in binary read mode. The returned
        object should be closed when finished reading.
        """
        path = self._getpath(name, bucket)
        if not exists(path):
            raise NotFound(name, bucket)
        return open(path, "rb")

    def delete(self, name=None, bucket=DEFAULT_BUCKET):
        """Delete a blob

        :param name: The name of the object to be deleted. The entire
        bucket will be deleted if this is not specified.
        :param bucket: Optional bucket name. This must have the same
        value that was passed to ``put``.
        :returns: True if the blob was deleted else false.
        """
        if name is None:
            assert not bucket.startswith(("/", "\\")), bucket
            path = join(self.rootdir, bucket)
            remove = shutil.rmtree
        else:
            path = self._getpath(name, bucket)
            remove = os.remove
        if not exists(path):
            return False
        remove(path)
        return True

    def _getpath(self, name, bucket):
        assert not bucket.startswith(("/", "\\")), bucket
        assert not name.startswith(("/", "\\")), name
        root = join(self.rootdir, bucket)
        if isinstance(name, unicode):
            name = name.encode("utf-8")
        hashname = md5(name).hexdigest()
        return join(root, hashname)


class Error(Exception):
    """BlobDB error"""


class NotFound(Error):
    """Raised when an attachment cannot be found"""
