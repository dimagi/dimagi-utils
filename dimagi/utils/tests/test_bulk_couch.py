from django.test import SimpleTestCase
from dimagi.utils.couch.bulk import IterativeSaver


class LoggingDB(object):
    def __init__(self):
        self.docs_saved = []

    def bulk_save(self, docs):
        self.docs_saved.extend(docs)


class IterativeSaverTest(SimpleTestCase):

    def test_iter_save(self):
        db = LoggingDB()
        all_docs = range(10)
        with IterativeSaver(db, chunksize=3) as iter_db:
            for doc in all_docs:
                iter_db.save(doc)

        # the saver should have cleared out all the docs
        self.assertEqual(iter_db.to_save, [])

        # The db should have saved all the docs
        self.assertEqual(all_docs, db.docs_saved)
