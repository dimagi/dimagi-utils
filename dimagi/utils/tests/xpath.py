from django.test import TestCase
from ..xpath import dot_interpolate


class DotInterpolateTest(TestCase):

    def testRegex(self):
        replacement = "@case_id stuff"
        cases = [
            ('./lmp < 570.5', '%s/lmp < 570.5'),
            ('stuff ./lmp < 570.', 'stuff %s/lmp < 570.'),
            ('.53 < hello.', '.53 < hello%s'),
        ]
        for case in cases:
            self.assertEqual(
                dot_interpolate(replacement, case[0]),
                case[1] % replacement
            )
