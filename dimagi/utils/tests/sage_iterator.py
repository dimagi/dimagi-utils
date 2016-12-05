from django.test import SimpleTestCase

from dimagi.utils.safe_iterator import SafeIterator, IteratorAlreadyConsumedException, safe_generator


class SafeIteratorTest(SimpleTestCase):

    def test_exception(self):
        generator = (x for x in range(3))
        safe_generator = SafeIterator(generator)
        self.assertEqual(list(safe_generator), [0, 1, 2])
        with self.assertRaises(IteratorAlreadyConsumedException):
            for i in safe_generator:
                pass

    def test_decorator(self):
        @safe_generator
        def func():
            return (x for x in range(3))

        generator = func()
        self.assertEqual(list(generator), [0, 1, 2])
        with self.assertRaises(IteratorAlreadyConsumedException):
            list(generator)
