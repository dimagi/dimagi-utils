import os
from hashlib import md5
from itertools import count
from shutil import rmtree
from tempfile import mkdtemp
from unittest import TestCase
from StringIO import StringIO

import dimagi.ext.attachments as mod
from dimagi.ext.blobdb import FilesystemBlobDB
from dimagi.ext.couchdbkit import Document
from dimagi.ext.tests.util import generate_cases


class TestBlobMixin(TestCase):

    keys = (md5(str(k)).hexdigest() for k in count())

    @classmethod
    def setUpClass(cls):
        cls.rootdir = mkdtemp(prefix="blobdb")
        cls.db = FilesystemBlobDB(cls.rootdir)

    @classmethod
    def tearDownClass(cls):
        cls.db = None
        rmtree(cls.rootdir)
        cls.rootdir = None

    def setUp(self):
        doc = {
            "_id": next(self.keys),
            "_rev": next(self.keys),
        }
        self.obj = FakeCouchDocument(doc, self.db)

    def test_put_attachment_without_name(self):
        with self.assertRaises(mod.InvalidAttachment):
            self.obj.put_attachment("content")

    def test_put_attachment_unicode(self):
        name = "test.1"
        data = u"\u4500 content"
        self.obj.put_attachment(data, name)
        self.assertEqual(self.obj.fetch_attachment(name), data)

    def test_put_attachment_bytes(self):
        name = "test.1"
        data = b"\xe4\x94 content" # cannot be decoded as UTF-8
        self.obj.put_attachment(data, name)
        self.assertEqual(self.obj.fetch_attachment(name), data)

    def test_put_attachment_with_named_content(self):
        content = StringIO(b"content")
        content.name = "test.1"
        self.obj.put_attachment(content)
        self.assertEqual(self.obj.fetch_attachment(content.name), "content")

    def test_fetch_attachment_with_unicode(self):
        name = "test.1"
        content = u"\u4500 is not ascii"
        self.obj.put_attachment(content, name)
        self.assertEqual(self.obj.fetch_attachment(name), content)

    def test_fetch_attachment_stream(self):
        name = "test.1"
        content = u"\u4500 is not ascii"
        self.obj.put_attachment(content, name)
        with self.obj.fetch_attachment(name, stream=True) as fh:
            self.assertEqual(fh.read().decode("utf-8"), content)

    def test_delete_attachment(self):
        name = u"test.\u4500"
        content = u"\u4500 is not ascii"
        self.obj.put_attachment(content, name)
        self.obj.delete_attachment(name)
        with self.assertRaises(mod.ResourceNotFound):
            self.obj.fetch_attachment(name)

    def test_document_blobs(self):
        name = "test.1"
        content = StringIO(b"content")
        self.obj.put_attachment(content, name, content_type="text/plain")
        self.assertEqual(self.obj.blobs[name].content_type, "text/plain")
        self.assertEqual(self.obj.blobs[name].content_length, 7)

@generate_cases([
    (None, None),
    ("abc", None),
    (None, "abc"),
], TestBlobMixin)
def test_unsaved_document(self, _id, _rev):
    doc = {"_id": _id, "_rev": _rev}
    obj = FakeCouchDocument(doc, self.db)
    with self.assertRaises(mod.ResourceNotFound):
        obj.put_attachment(b"content", "test.1")


class FakeCouchDocument(mod.BlobMixin, Document):
    doc_type = "FakeCouchDocument"

    def __init__(self, doc, blobdb):
        super(FakeCouchDocument, self).__init__()
        self._doc.update(doc)
        self._blobdb = blobdb
