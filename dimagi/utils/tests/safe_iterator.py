from django.test import SimpleTestCase

from dimagi.utils.couch.database import multi_use_generator


class SafeIteratorTest(SimpleTestCase):

    def test_decorator(self):

        @multi_use_generator
        def func():
            return (x for x in range(3))

        generator = func()
        self.assertEqual(list(generator), [0, 1, 2])
        self.assertEqual(list(generator), [0, 1, 2])
