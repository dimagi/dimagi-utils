from django.test import SimpleTestCase

from dimagi.utils.couch.database import SafeGenerator, GeneratorAlreadyConsumedException


class SafeGeneratorTest(SimpleTestCase):

    def test_exception(self):
        generator = (x for x in range(3))
        safe_generator = SafeGenerator(generator)
        self.assertEqual(list(safe_generator), [0,1,2])
        with self.assertRaises(GeneratorAlreadyConsumedException):
            for i in safe_generator:
                pass
