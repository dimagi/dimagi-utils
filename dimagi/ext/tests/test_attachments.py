import os
from hashlib import md5
from itertools import count
from shutil import rmtree
from tempfile import mkdtemp
from unittest import TestCase
from StringIO import StringIO

import dimagi.ext.attachments as mod
from dimagi.ext.blobdb import FilesystemBlobDB


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
        doc = {"_id": next(self.keys)}
        self.obj = FakeCouchDocument(doc, self.db)

    def test_put_attachment_without_name(self):
        with self.assertRaises(mod.InvalidAttachment):
            self.obj.put_attachment("content")

    def test_put_attachment(self):
        name = "test.1"
        self.obj.put_attachment(StringIO("content"), name)
        self.assertEqual(self.obj.fetch_attachment(name), "content")

    def test_put_attachment_with_named_content(self):
        name = "test.1"
        content = StringIO("content")
        content.name = name
        self.obj.put_attachment(content)
        self.assertEqual(self.obj.fetch_attachment(name), "content")

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


class FakeCouchDocument(mod.BlobMixin):

    def __init__(self, doc, blobdb):
        self._doc = doc
        self._blobdb = blobdb
